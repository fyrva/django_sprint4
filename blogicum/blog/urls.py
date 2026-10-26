from django.urls import path
from django.contrib.auth import get_user_model
from . import views


User = get_user_model()

app_name = 'blog'

urlpatterns = [
    path('', views.PostsListView.as_view(), name='index'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path(
        'posts/<int:post_id>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
        ),
    path('posts/<int:post_id>/comment/',
         views.create_comment,
         name='add_comment'
         ),
    path('posts/<int:post_id>/edit_comment/<int:pk>/',
         views.CommentUpdateView.as_view(),
         name='edit_comment'
         ),
    path('posts/<int:post_id>/delete_comment/<int:pk>/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'
         ),
    path('posts/<int:post_id>/delete/',
         views.PostDeleteView.as_view(),
         name='delete_post'
         ),
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'
        ),
    path(
        'profile/edit/',
        views.UserUpdateView.as_view(),
        name='edit_profile'
    ),
    path(
        'profile/<slug:username>/',
        views.profile,
        name='profile'
    ),
    path(
        'posts/create/',
        views.PostCreateView.as_view(),
        name='create_post'
    )
]
