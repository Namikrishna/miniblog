from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('blog/', views.IndexView.as_view(), name='blog-home'),
    path('blog/blogs/', views.BlogListView.as_view(), name='blog-list'),
    path('blog/<int:pk>/', views.BlogDetailView.as_view(), name='blog-detail'),
    path('blog/blogger/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    path('blog/bloggers/', views.AuthorListView.as_view(), name='author-list'),
    path('blog/<int:pk>/create/', views.CommentCreateView.as_view(), name='comment-create'),
    path('register/', views.register, name='register'),
    path('blog/create/', views.BlogCreateView.as_view(), name='blog-create'),
    path('dashboard/', views.AuthorDashboardView.as_view(), name='author-dashboard'),
    path('profile/update/', views.profile_update, name='profile-update'),
    path('profile/password/', views.CustomPasswordChangeView.as_view(), name='password-change'),
    path('blog/<int:pk>/delete/', views.BlogDeleteView.as_view(), name='blog-delete'),
    path('comment/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment-delete'),
    # Review URLs
    path('blog/<int:pk>/review/', views.ReviewCreateView.as_view(), name='review-create'),
    path('review/<int:pk>/update/', views.ReviewUpdateView.as_view(), name='review-update'),
    path('review/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review-delete'),
    path('blog/<int:pk>/rate/', views.rate_blog, name='rate-blog'),
    # Like URLs
    path('blog/<int:pk>/like/', views.like_blog, name='like-blog'),
] 