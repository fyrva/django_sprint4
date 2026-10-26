from django.shortcuts import render, get_object_or_404
from blog.models import Post, Category, Comment
from django.db.models import Q
from datetime import datetime
from django.core.paginator import Paginator
from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from .forms import UserEditForm, PostCreateForm, CommentCreateForm
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


User = get_user_model()


def post_detail(request, post_id):
    """Обрабатывает запрос на просмотр публикации."""
    template = 'blog/detail.html'
    post_author = get_object_or_404(Post, pk=post_id).author
    if request.user != post_author:
        post = get_object_or_404(
                Post,
                pk=post_id,
                is_published=True,
                category__is_published=True,
                pub_date__lte=datetime.now().astimezone()
            )
    else:
        post = get_object_or_404(
            Post,
            pk=post_id
        )

    comments = (post.comments.all()
                .select_related('author')
                .order_by('created_at')
                )
    context = {
        'post': post,
        'comments': comments
        }

    if request.user.is_authenticated:
        form = CommentCreateForm()
        context['form'] = form

    return render(request, template, context)


def category_posts(request, category_slug):
    """Обрабатывает запрос на просмотр категории."""
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = Post.objects.select_related(
        'location',
        'author',
        'category'
    ).filter(
        Q(is_published=True)
        & Q(category=category)
    ).filter(
        pub_date__lte=datetime.now().astimezone()
    ).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'post_list': post_list,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """Обрабатывает запрос на просмотр профиля."""
    template_name = 'blog/profile.html'
    profile = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author_id=profile.id)
    if request.user != profile:
        post_list = post_list.filter(
            Q(is_published=True)
            & Q(category__is_published=True)
        ).filter(
            pub_date__lte=datetime.now().astimezone()
        )
    post_list = post_list.order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': profile,
        'page_obj': page_obj
        }
    return render(request, template_name, context)


@login_required
def create_comment(request, post_id):
    """Функция для создания комментария."""
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.author = request.user
            obj.post = post
            obj.save()

    return redirect(
        'blog:post_detail',
        post_id
        )


class PostsListView(ListView):
    """CBV для списка публикаций."""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10
    queryset = Post.objects.select_related(
        'location',
        'author',
        'category'
    ).filter(
        Q(is_published=True)
        & Q(category__is_published=True)
    ).filter(
        pub_date__lte=datetime.now().astimezone()
    ).order_by('-pub_date')


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """CBV для изменения данных пользователя."""

    model = User
    form_class = UserEditForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        """Использует пользователя который отправляет запрос."""
        return self.request.user


class PostCreateView(CreateView):
    """CBV для создания публикации."""

    form_class = PostCreateForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        """Проверка пользователя на авторизацию."""
        if not request.user.is_authenticated:
            return redirect('blog:index')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Указывает автором поста пользователя, который отправил запрос."""
        obj = form.save(commit=False)
        obj.author = self.request.user
        obj.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Перенаправляет на страницу автора."""
        return reverse_lazy('blog:profile', args=(self.request.user.username,))


class PostUpdateView(UpdateView):
    """CBV для изменения поста."""

    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        """Проверка на авторизацию пользователя."""
        if (
            not request.user.is_authenticated or
            request.user != self.get_object().author
        ):
            post_id = self.kwargs.get('post_id')
            return redirect('blog:post_detail', post_id=post_id)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Указывает автором поста пользователя, который отправил запрос."""
        obj = form.save(commit=False)
        obj.author = self.request.user
        obj.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Перенаправляет на страницу автора."""
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.object.id}
            )


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    """CBV для изменения комментария."""

    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentCreateForm

    def dispatch(self, request, *args, **kwargs):
        """Проверка на авторство комментария."""
        if request.user != self.get_object().author:
            raise PermissionDenied("Вы не являетесь автором комментария!")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Указывает автором поста пользователя, который отправил запрос."""
        obj = form.save(commit=False)
        obj.author = self.request.user
        obj.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Перенаправляет на страницу автора."""
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.object.post_id}
            )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    """CBV для удаления комментария."""

    model = Comment
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        """Проверка на авторство комментария."""
        if request.user != self.get_object().author:
            raise PermissionDenied("Вы не являетесь автором комментария!")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """Перенаправляет на публикацию, к которой относился комментарий."""
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.object.post_id}
        )


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """CBV для удаления публикации."""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        """Проверка на авторизацию пользователя."""
        if (
            not request.user.is_authenticated or
            request.user != self.get_object().author
        ):
            post_id = self.kwargs.get('post_id')
            return redirect('blog:post_detail', post_id=post_id)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """Перенаправлет на страницу пользователя."""
        return reverse_lazy('blog:profile', args=(self.request.user.username,))
