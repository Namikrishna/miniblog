from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, help_text="Enter your biography", blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.png')
    
    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])
    
    def __str__(self):
        return self.user.username

class Like(models.Model):
    LIKE_CHOICES = (
        (1, 'Like'),
        (-1, 'Dislike'),
    )
    
    blog = models.ForeignKey('Blog', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField(choices=LIKE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['blog', 'user']

    def __str__(self):
        return f"{self.user.username}'s {'like' if self.value == 1 else 'dislike'} for {self.blog.title}"

class Blog(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    content = models.TextField(help_text="Write your blog content here")
    post_date = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    audio = models.FileField(upload_to='blog_audio/', null=True, blank=True, help_text='Upload an audio file (MP3, WAV)')
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_ratings = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    dislikes_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-post_date']
    
    def get_absolute_url(self):
        return reverse('blog-detail', args=[str(self.id)])
    
    def __str__(self):
        return self.title

    def update_rating(self):
        ratings = self.rating_set.all()
        if ratings.exists():
            self.average_rating = sum(rating.value for rating in ratings) / ratings.count()
            self.total_ratings = ratings.count()
        else:
            self.average_rating = 0.00
            self.total_ratings = 0
        self.save()

    def update_likes_count(self):
        self.likes_count = self.like_set.filter(value=1).count()
        self.dislikes_count = self.like_set.filter(value=-1).count()
        self.save()

class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000, help_text="Enter your comment")
    post_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['post_date']
    
    def __str__(self):
        return f'{self.content[:75]}...' if len(self.content) > 75 else self.content

class Review(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('blog', 'user')  # One review per user per blog

    def __str__(self):
        return f'Review by {self.user.username} on {self.blog.title}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.blog.update_rating()

class Rating(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['blog', 'user']

    def __str__(self):
        return f"{self.user.username}'s rating for {self.blog.title}"
