from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Prefetch
from blog.models import Comment, Post, Tag


def serialize_post(post):
    first_tag = post.tags.first()
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': getattr(post, 'comments_count', 0),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': first_tag.title if first_tag else '',
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count if hasattr(tag, 'posts_count') else tag.posts.count(),
    }


def index(request):
    tags_prefetch = Prefetch(
        'tags',
        queryset=Tag.objects.with_posts_count()
    )

    popular_posts = Post.objects.popular()\
                        .select_related('author')\
                        .prefetch_related(tags_prefetch)[:5]\
                        .fetch_with_comments_count()

    fresh_posts = Post.objects.order_by('-published_at')\
                    .select_related('author')\
                    .prefetch_related(tags_prefetch)[:5]\
                    .fetch_with_comments_count()

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [serialize_post(post) for post in popular_posts],
        'page_posts': [serialize_post(post) for post in fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    tags_prefetch = Prefetch(
        'tags',
        queryset=Tag.objects.with_posts_count()
    )

    post = get_object_or_404(
        Post.objects.select_related('author').prefetch_related(tags_prefetch),
        slug=slug
    )

    comments = Comment.objects.filter(post=post).select_related('author')
    serialized_comments = [{
        'text': comment.text,
        'published_at': comment.published_at,
        'author': comment.author.username,
    } for comment in comments]

    likes = post.likes.all()

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': len(likes),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
    }

    most_popular_tags = Tag.objects.popular()[:5]
    most_popular_posts = Post.objects.popular()\
                           .select_related('author')\
                           .prefetch_related(tags_prefetch)[:5]\
                           .fetch_with_comments_count()

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = get_object_or_404(Tag, title=tag_title)

    tags_prefetch = Prefetch(
        'tags',
        queryset=Tag.objects.with_posts_count()
    )

    most_popular_tags = Tag.objects.popular()[:5]
    most_popular_posts = Post.objects.popular()\
                           .select_related('author')\
                           .prefetch_related(tags_prefetch)[:5]\
                           .fetch_with_comments_count()

    related_posts = tag.posts.all()\
                     .select_related('author')\
                     .prefetch_related(tags_prefetch)[:20]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    return render(request, 'contacts.html', {})
