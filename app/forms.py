from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Blog, Author, Review, Rating

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

class BlogForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your blog title'
        }),
        help_text='Give your blog post a catchy title'
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Write your blog content here...',
            'style': 'min-height: 300px;'
        }),
        help_text='Write your blog post content using markdown or plain text'
    )
    image = forms.ImageField(required=False)
    audio = forms.FileField(required=False)

    class Meta:
        model = Blog
        fields = ['title', 'content', 'image', 'audio']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title.strip()) < 5:
            raise forms.ValidationError("Title must be at least 5 characters long")
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 100:
            raise forms.ValidationError("Content must be at least 100 characters long")
        return content

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class AuthorProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['bio', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'})
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['value']
        widgets = {
            'value': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '5',
                'type': 'number'
            })
        } 