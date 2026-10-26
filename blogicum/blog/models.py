from django.db import models
from core.models import BaseModel
from django.contrib.auth import get_user_model


User = get_user_model()


class Post(BaseModel):
    """Модель публикации."""

    title = models.CharField(
        max_length=256,
        null=False,
        verbose_name='Заголовок'
    )
    text = models.TextField(
        null=False,
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        null=False,
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем '
        + '— можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        null=False,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )

    image = models.ImageField('Фото', upload_to='posts_images', blank=True)

    class Meta:
        """Переопределение класса Meta Model."""

        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        """Возвращает заголовок публикации."""
        return self.title

    @property
    def comment_count(self):
        """Свойство возвращающее количество комментариев к посту."""
        return self.comments.count()


class Category(BaseModel):
    """Модель категории."""

    title = models.CharField(
        max_length=256,
        null=False,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        null=False,
        verbose_name='Описание'
    )
    slug = models.SlugField(
        unique=True,
        null=False,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
        + 'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        """Переопределение класса Meta Model."""

        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        """Возвращает название категории."""
        return self.title


class Location(BaseModel):
    """Класс модели места."""

    name = models.CharField(
        max_length=256,
        null=False,
        verbose_name='Название места'
    )

    class Meta:
        """Переопределение класса Meta Model."""

        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        """Возвращает название места."""
        return self.name


class Comment(BaseModel):
    """Класс модели комментария."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
        )
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True
    )

    class Meta:
        """Переопределение класса Meta Model."""

        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        """Возвращает логин автора и первое слово комментария."""
        return f'{self.author.username}: {self.text[0]}...'
