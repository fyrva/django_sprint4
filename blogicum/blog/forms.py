from django.contrib.auth import get_user_model
from django.forms import ModelForm
from .models import Post, Comment
from django.forms.widgets import DateTimeInput, Textarea


User = get_user_model()


class UserEditForm(ModelForm):
    """Класс формы для изменения данных о пользователе."""

    class Meta:
        """Переопределение класса Meta ModelForm."""

        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email'
            )


class PostCreateForm(ModelForm):
    """Класс формы для создания и изменения публикации."""

    class Meta:
        """Переопределение класса Meta ModelForm."""

        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%d %H:%M:%S',
                )
            }


class CommentCreateForm(ModelForm):
    """Класс формы для создания и изменения комментария."""

    class Meta:
        """Переопределение класса Meta ModelForm."""

        model = Comment
        exclude = ('author', 'post')
        widgets = {
            'text': Textarea()
        }
