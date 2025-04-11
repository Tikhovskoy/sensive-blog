from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.contrib.auth.models import User

class PostQuerySet(models.QuerySet):
    def year(self, year):
        return self.filter(published_at__year=year)

    def popular(self):
        return self.annotate(likes_count=Count('likes', distinct=True)).order_by('-likes_count')
    
    def fetch_with_comments_count(self):
        posts = list(self)
        from blog.models import Comment
        post_ids = [post.id for post in posts]
        comments = Comment.objects.filter(post_id__in=post_ids)\
                                  .values('post_id')\
                                  .annotate(count=Count('id', distinct=True))
        comments_map = {item['post_id']: item['count'] for item in comments}
        for post in posts:
            post.comments_count = comments_map.get(post.id, 0)
        return posts

class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)
    
    def year(self, year):
        return self.get_queryset().year(year)
    
    def popular(self):
        return self.get_queryset().popular()

class Post(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    slug = models.SlugField('Название в виде url', max_length=200)
    image = models.ImageField('Картинка')
    published_at = models.DateTimeField('Дата и время публикации')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        limit_choices_to={'is_staff': True})
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        verbose_name='Кто лайкнул',
        blank=True)
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        verbose_name='Теги')

    objects = PostManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'


class TagQuerySet(models.QuerySet):
    def popular(self):
        return self.annotate(posts_count=Count('posts', distinct=True)).order_by('-posts_count')

class TagManager(models.Manager):
    def get_queryset(self):
        return TagQuerySet(self.model, using=self._db)
    
    def popular(self):
        return self.get_queryset().popular()

class Tag(models.Model):
    title = models.CharField('Тег', max_length=20, unique=True)

    objects = TagManager() 

    def __str__(self):
        return self.title

    def clean(self):
        self.title = self.title.lower()

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})

    class Meta:
        ordering = ['title']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments', 
        verbose_name='Пост, к которому написан')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор')
    text = models.TextField('Текст комментария')
    published_at = models.DateTimeField('Дата и время публикации')

    def __str__(self):
        return f'{self.author.username} under {self.post.title}'

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
