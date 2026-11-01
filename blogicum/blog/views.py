from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post

User = get_user_model()

POSTS_PER_PAGE = 10


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


def paginate(request, queryset):
    return Paginator(queryset, POSTS_PER_PAGE).get_page(
        request.GET.get('page')
    )


def index(request):
    return render(
        request,
        'blog/index.html',
        {'page_obj': paginate(request, get_posts())},
    )


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True
    )
    return render(
        request,
        'blog/category.html',
        {
            'category': category,
            'page_obj': paginate(request, get_posts(category.posts)),
        },
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = get_posts(
        author.posts, published_only=request.user != author
    )
    return render(
        request,
        'blog/profile.html',
        {'profile': author, 'page_obj': paginate(request, posts)},
    )


@login_required
def edit_profile(request):
    form = UserForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', request.user.username)
    return render(request, 'blog/user.html', {'form': form})


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


def post_detail(request, post_id):
    post = get_visible_post(request, post_id)
    return render(
        request,
        'blog/detail.html',
        {
            'post': post,
            'form': CommentForm(),
            'comments': post.comments.select_related('author'),
        },
    )


@login_required
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', request.user.username)
    return render(request, 'blog/create.html', {'form': form})


def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id, author=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', request.user.username)
    return render(
        request, 'blog/create.html', {'form': PostForm(instance=post)}
    )


@login_required
def add_comment(request, post_id):
    post = get_visible_post(request, post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment, pk=comment_id, post_id=post_id, author=request.user
    )
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    return render(
        request, 'blog/comment.html', {'form': form, 'comment': comment}
    )


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment, pk=comment_id, post_id=post_id, author=request.user
    )
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/comment.html', {'comment': comment})
