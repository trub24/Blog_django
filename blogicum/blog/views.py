from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.views.generic import (
    CreateView, UpdateView, DeleteView, ListView, DetailView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.urls import reverse_lazy, reverse
from blog.models import Post, Category, Comment, User
from blog.forms import PostForm, CommentForm, ProfileForm
from blog.mixins import OnlyAuthorMixin


PAGE_NUM = 10


def post_object(slug=None):
    posts = Post.objects.select_related(
        'location', 'category', 'author',
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lt=now(),
    )
    if slug:
        posts = posts.filter(category__slug=slug)
    return posts


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    queryset = post_object().annotate(comment_count=Count('Comments'))
    paginate_by = PAGE_NUM
    ordering = '-pub_date'


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if post.author != self.request.user:
            post = get_object_or_404(post_object(), pk=self.kwargs['post_id'])
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.select_related(
            'author'
        ).filter(post__id=self.kwargs['post_id'])
        return context


class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category.html'
    slug_url_kwarg = 'category_slug'
    paginate_by = PAGE_NUM

    def get_queryset(self):
        return post_object(self.kwargs['category_slug']).annotate(
            comment_count=Count('Comments')
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category.objects.values(
            'title', 'description', 'id'
        ), slug=self.kwargs['category_slug'], is_published=True)
        return context


class PostMixin:
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    form_class = PostForm
    success_url = reverse_lazy('blog:profile')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostUpdateView(OnlyAuthorMixin, PostMixin, UpdateView):
    form_class = PostForm


class PostDeleteView(OnlyAuthorMixin, PostMixin, DeleteView):
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class ProfileListView(ListView):
    model = User
    template_name = 'blog/profile.html'
    pk_url_kwarg = 'username'
    paginate_by = PAGE_NUM

    def get_queryset(self):
        return Post.objects.select_related(
            'location', 'category', 'author',
        ).filter(
            author__username=self.kwargs['username']
        ).annotate(
            comment_count=Count('Comments')
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs['username']
        )
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = ProfileForm
    success_url = reverse_lazy('blog:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class CommentMixin:
    model = Comment

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse('blog:post_detail', kwargs={'post_id': post_id})


class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentEditView(OnlyAuthorMixin, CommentMixin, UpdateView):
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'


class CommentDeleteView(OnlyAuthorMixin, CommentMixin, DeleteView):
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
