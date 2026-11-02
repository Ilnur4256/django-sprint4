from django.contrib import admin
from django.utils.html import format_html

from .constants import ADMIN_IMAGE_THUMB_WIDTH
from .models import Category, Comment, Location, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'image_preview',
        'author',
        'category',
        'location',
        'pub_date',
        'is_published',
    )
    list_editable = ('is_published', 'category')
    list_filter = ('is_published', 'category', 'location')
    search_fields = ('title', 'text')
    date_hierarchy = 'pub_date'
    readonly_fields = ('image_preview', 'created_at')
    fieldsets = (
        ('Содержание', {
            'fields': ('title', 'text', 'image', 'image_preview'),
        }),
        ('Привязки', {
            'fields': ('author', 'category', 'location'),
        }),
        ('Публикация', {
            'fields': ('pub_date', 'is_published', 'created_at'),
        }),
    )

    @admin.display(description='Изображение')
    def image_preview(self, post):
        if post.image:
            return format_html(
                '<img src="{}" width="{}">',
                post.image.url,
                ADMIN_IMAGE_THUMB_WIDTH,
            )
        return '—'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'post', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text',)
