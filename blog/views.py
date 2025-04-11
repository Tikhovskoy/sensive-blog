from django.shortcuts import render
from django.db.models import Count
from blog.models import Comment, Post, Tag


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': len(Comment.objects.filter(post=post)),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title if post.tags.all() else '',
    }


def serialize_post_optimized(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title if post.tags.all() else '',
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts.count(),
    }


def index(request):
    popular_posts = list(
        Post.objects.annotate(
            likes_count=Count('likes', distinct=True)
        )
        .order_by('-likes_count')
        .select_related('author')
        .prefetch_related('tags')[:5]
    )

    popular_post_ids = [post.id for post in popular_posts]
    popular_comments = Comment.objects.filter(post_id__in=popular_post_ids) \
        .values('post_id') \
        .annotate(count=Count('id'))
    comments_map_popular = {item['post_id']: item['count'] for item in popular_comments}
    for post in popular_posts:
        post.comments_count = comments_map_popular.get(post.id, 0)

    fresh_posts = list(
        Post.objects.order_by('-published_at')
        .select_related('author')
        .prefetch_related('tags')[:5]
    )
    
    fresh_post_ids = [post.id for post in fresh_posts]
    fresh_comments = Comment.objects.filter(post_id__in=fresh_post_ids) \
        .values('post_id') \
        .annotate(count=Count('id'))
    comments_map_fresh = {item['post_id']: item['count'] for item in fresh_comments}
    for post in fresh_posts:
        post.comments_count = comments_map_fresh.get(post.id, 0)

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [serialize_post_optimized(post) for post in popular_posts],
        'page_posts': [serialize_post_optimized(post) for post in fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = Post.objects.select_related('author').prefetch_related('tags').get(slug=slug)
    comments = Comment.objects.filter(post=post).select_related('author')
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

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

    most_popular_posts = (
        Post.objects.annotate(likes_count=Count('likes', distinct=True))
        .order_by('-likes_count')
        .select_related('author')
        .prefetch_related('tags')
        [:5]
    )

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    most_popular_tags = Tag.objects.popular()[:5]

    most_popular_posts = (
        Post.objects.annotate(likes_count=Count('likes', distinct=True))
        .order_by('-likes_count')
        .select_related('author')
        .prefetch_related('tags')
        [:5]
    )

    related_posts = (
        tag.posts.all()
        .select_related('author')
        .prefetch_related('tags')
        [:20]
    )

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    return render(request, 'contacts.html', {})
