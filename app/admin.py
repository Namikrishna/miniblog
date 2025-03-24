from django.contrib import admin
from .models import Author, Blog, Comment

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('post_date',)
    fields = ('user', 'content', 'post_date')
    ordering = ['post_date']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'post_date', 'comment_count')
    list_filter = ('post_date', 'author')
    search_fields = ('title', 'content')
    inlines = [CommentInline]
    readonly_fields = ('post_date',)
    
    def comment_count(self, obj):
        return obj.comment_set.count()
    comment_count.short_description = 'Comments'

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'post_count')
    search_fields = ('user__username', 'bio')
    list_select_related = ('user',)
    
    def post_count(self, obj):
        return obj.blog_set.count()
    post_count.short_description = 'Number of Posts'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('truncated_content', 'blog', 'user', 'post_date')
    list_filter = ('post_date', 'user', 'blog')
    search_fields = ('content', 'user__username', 'blog__title')
    readonly_fields = ('post_date',)
    list_select_related = ('user', 'blog')
    
    def truncated_content(self, obj):
        return obj.content[:75] + '...' if len(obj.content) > 75 else obj.content
    truncated_content.short_description = 'Comment'
