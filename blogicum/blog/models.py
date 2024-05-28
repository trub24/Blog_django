from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class CoreBlogModel(models.Model):
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        abstract = True


class Location(CoreBlogModel):
    name = models.CharField('Название места', max_length=256)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Category(CoreBlogModel):
    title = models.CharField('Заголовок', max_length=256)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        help_text=('Идентификатор страницы для URL; разрешены символы '
                   'латиницы, цифры, дефис и подчёркивание.'),
        unique=True
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Post(CoreBlogModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Автор публикации')
    title = models.CharField('Заголовок', max_length=256)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=('Если установить дату и время в '
                   'будущем — можно делать отложенные публикации.')
    )
    location = models.ForeignKey(Location, null=True, blank=True,
                                 on_delete=models.SET_NULL,
                                 related_name='post_location',
                                 verbose_name='Местоположение')
    category = models.ForeignKey(Category, null=True,
                                 on_delete=models.SET_NULL,
                                 related_name='posts_in_category',
                                 verbose_name='Категория')
    image = models.ImageField('Изображение', blank=True)

    class Meta:
        default_related_name = 'post'
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.pk})


class Comment(CoreBlogModel):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Публикация'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )

    class Meta:
        default_related_name = 'Comments'
        verbose_name = 'коментарий'
        verbose_name_plural = 'Коментарии'
        ordering = ('created_at',)

    def __str__(self):
        return self.text
