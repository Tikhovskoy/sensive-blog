from django.contrib import admin
from blog.models import Post, Tag, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at', 'author')
    raw_id_fields = ('author',)
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'published_at', 'text')
    raw_id_fields = ('post', 'author')
    list_filter = ('published_at',)
