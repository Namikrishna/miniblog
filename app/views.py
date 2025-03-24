from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView
from .models import Blog, Author, Comment, Review, Rating, Like
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import UserRegistrationForm, BlogForm, UserProfileUpdateForm, AuthorProfileUpdateForm, CustomPasswordChangeForm, ReviewForm, RatingForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q, Count
from django.views.decorators.http import require_POST

# Create your views here.

class IndexView(generic.TemplateView):
    template_name = 'app/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_blogs'] = Blog.objects.all().order_by('-post_date')[:4]
        return context

class BlogListView(generic.ListView):
    model = Blog
    template_name = 'app/blog_list.html'
    context_object_name = 'blogs'
    ordering = ['-post_date']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(author__user__username__icontains=search_query)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        
        # Add recent blogs
        context['recent_blogs'] = Blog.objects.all().order_by('-post_date')[:5]
        
        # Add popular authors (authors with most posts)
        context['popular_authors'] = Author.objects.annotate(
            post_count=Count('blog')
        ).order_by('-post_count')[:5]
        
        return context

class BlogDetailView(generic.DetailView):
    model = Blog
    template_name = 'app/blog_detail.html'
    context_object_name = 'blog'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blog = self.get_object()
        
        # Get user's review if they have one
        if self.request.user.is_authenticated:
            context['user_review'] = Review.objects.filter(
                blog=blog,
                user=self.request.user
            ).first()
            
            # Get user's rating if they have one
            context['user_rating'] = Rating.objects.filter(
                blog=blog,
                user=self.request.user
            ).first()
            
            # Get all reviews except user's own
            context['reviews'] = Review.objects.filter(
                blog=blog
            ).exclude(
                user=self.request.user
            ).order_by('-created_at')
        else:
            context['user_review'] = None
            context['user_rating'] = None
            context['reviews'] = Review.objects.filter(
                blog=blog
            ).order_by('-created_at')
        
        return context

class AuthorListView(generic.ListView):
    model = Author
    template_name = 'app/author_list.html'
    context_object_name = 'authors'

class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'app/author_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blogs'] = Blog.objects.filter(author=self.object).order_by('-post_date')
        return context

@method_decorator(login_required, name='dispatch')
class CommentCreateView(CreateView):
    model = Comment
    fields = ['content']
    template_name = 'app/comment_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.blog = get_object_or_404(Blog, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('app:blog-detail', kwargs={'pk': self.kwargs['pk']})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Get or create Author profile for the user
            Author.objects.get_or_create(
                user=user,
                defaults={'bio': ''}
            )
            messages.success(request, f'Account created successfully! Please login to continue.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@method_decorator(login_required, name='dispatch')
class BlogCreateView(CreateView):
    model = Blog
    form_class = BlogForm
    template_name = 'app/blog_form.html'
    
    def form_valid(self, form):
        # Get or create the author profile for the current user
        author, created = Author.objects.get_or_create(
            user=self.request.user,
            defaults={'bio': ''}
        )
        form.instance.author = author
        messages.success(self.request, 'Blog post created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('app:blog-detail', kwargs={'pk': self.object.pk})

# Add a view to show author's dashboard with their posts
@method_decorator(login_required, name='dispatch')
class AuthorDashboardView(generic.TemplateView):
    template_name = 'app/author_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = Author.objects.get(user=self.request.user)
        context['blogs'] = Blog.objects.filter(author=author).order_by('-post_date')
        return context

@login_required
def profile_update(request):
    if request.method == 'POST':
        user_form = UserProfileUpdateForm(request.POST, instance=request.user)
        author_form = AuthorProfileUpdateForm(request.POST, request.FILES, instance=request.user.author)
        if user_form.is_valid() and author_form.is_valid():
            user_form.save()
            author_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('app:author-dashboard')
    else:
        user_form = UserProfileUpdateForm(instance=request.user)
        author_form = AuthorProfileUpdateForm(instance=request.user.author)
    
    return render(request, 'app/profile_update.html', {
        'user_form': user_form,
        'author_form': author_form
    })

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'app/password_change.html'
    success_url = reverse_lazy('app:author-dashboard')

    def form_valid(self, form):
        messages.success(self.request, 'Your password has been changed successfully!')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class CommentDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Comment
    template_name = 'app/comment_confirm_delete.html'

    def get_object(self, queryset=None):
        comment = super().get_object(queryset)
        if comment.user != self.request.user:
            return HttpResponseForbidden()
        return comment

    def get_success_url(self):
        return reverse('app:blog-detail', kwargs={'pk': self.object.blog.pk})

@method_decorator(login_required, name='dispatch')
class BlogDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Blog
    template_name = 'app/blog_confirm_delete.html'

    def get_object(self, queryset=None):
        blog = super().get_object(queryset)
        if blog.author.user != self.request.user:
            return HttpResponseForbidden()
        return blog

    def get_success_url(self):
        return reverse('app:author-dashboard')

@method_decorator(login_required, name='dispatch')
class ReviewCreateView(CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'app/review_form.html'

    def form_valid(self, form):
        blog = get_object_or_404(Blog, pk=self.kwargs['pk'])
        form.instance.blog = blog
        form.instance.user = self.request.user
        messages.success(self.request, 'Your review has been added successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('app:blog-detail', kwargs={'pk': self.kwargs['pk']})

@method_decorator(login_required, name='dispatch')
class ReviewUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'app/review_form.html'

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse('app:blog-detail', kwargs={'pk': self.object.blog.pk})

@method_decorator(login_required, name='dispatch')
class ReviewDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Review
    template_name = 'app/review_confirm_delete.html'

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse('app:blog-detail', kwargs={'pk': self.object.blog.pk})

@login_required
def rate_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating, created = Rating.objects.update_or_create(
                blog=blog,
                user=request.user,
                defaults={'value': form.cleaned_data['value']}
            )
            blog.update_rating()
            messages.success(request, 'Your rating has been updated!')
            return redirect('app:blog-detail', pk=blog.pk)
    else:
        form = RatingForm()
    
    return render(request, 'app/rate_blog.html', {
        'form': form,
        'blog': blog
    })

@login_required
@require_POST
def like_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    value = int(request.POST.get('value', 0))
    
    if value in [1, -1]:
        like, created = Like.objects.update_or_create(
            blog=blog,
            user=request.user,
            defaults={'value': value}
        )
        blog.update_likes_count()
        
        return JsonResponse({
            'status': 'success',
            'likes_count': blog.likes_count,
            'dislikes_count': blog.dislikes_count
        })
    
    return JsonResponse({'status': 'error'}, status=400)
