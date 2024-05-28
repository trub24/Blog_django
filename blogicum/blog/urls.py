from django.urls import path
from blog.views import post_detail, category_posts, index, profile, add_comment
from blog import views


app_name = 'blog'

urlpatterns = [
    path('', index, name='index'),
    path('posts/<int:post_id>/', post_detail, name='post_detail'),
    path('category/<slug:category_slug>/', category_posts,
         name='category_posts'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path(
        'posts/<int:post_id>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
    path('profile/<slug:username>/', profile, name='profile'),
    path('profile_edit/',
         views.ProfileEditView.as_view(),
         name='edit_profile'),
    path('posts/<int:post_id>/comment/',
         add_comment, name='add_comment'),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>',
        views.CommentEditView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>',
        views.CommentDeleteView.as_view(),
        name='delete_comment'
    ),
]
