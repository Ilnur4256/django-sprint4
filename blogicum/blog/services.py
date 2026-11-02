from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .constants import POSTS_PER_PAGE
from .models import Post


def get_posts(posts=Post.objects, published_only=True, with_comments=True):
    """Базовый запрос публикаций.

    published_only — оставить только то, что видно всем посетителям;
    with_comments — добавить количество комментариев и сортировку.
    """
    posts = posts.select_related('author', 'location', 'category')
    if published_only:
        posts = posts.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )
    if with_comments:
        posts = posts.annotate(
            comment_count=Count('comments')
        ).order_by(*Post._meta.ordering)
    return posts


def paginate(request, queryset, per_page=POSTS_PER_PAGE):
    """Страница пагинатора для номера страницы из GET-параметра page."""
    return Paginator(queryset, per_page).get_page(request.GET.get('page'))


def get_visible_post(request, post_id):
    """Пост, доступный текущему пользователю.

    Автор видит свои публикации всегда, остальные — только опубликованные.
    """
    post = get_object_or_404(
        get_posts(published_only=False, with_comments=False), pk=post_id
    )
    if post.author != request.user:
        post = get_object_or_404(
            get_posts(with_comments=False), pk=post_id
        )
    return post
