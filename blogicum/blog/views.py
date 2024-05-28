from django.db.models.base import Model as Model
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from django.core.paginator import Paginator
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.urls import reverse_lazy, reverse
from blog.models import Post, Category, Comment, User
from blog.forms import PostForm, CommentForm, ProfileForm


PAGE_NUM = 10


def post_object(slug=None):
    posts = Post.objects.select_related(
        'location', 'category', 'author',
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lt=now(),
    )
    if slug is not None:
        posts = posts.filter(category__slug=slug)
    return posts


def index(request):
    post_list = post_object().annotate(
        comment_count=Count('Comments')
    ).order_by('-pub_date')
    paginator = Paginator(post_list, PAGE_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'blog/index.html'
    context = {'page_obj': page_obj}
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'blog/detail.html'
    profile = get_object_or_404(Post, pk=post_id)
    if profile.author == request.user:
        post = get_object_or_404(Post, pk=post_id)
    else:
        post = get_object_or_404(post_object(), pk=post_id)
    context = {"post": post}
    context['form'] = CommentForm()
    context['comments'] = Comment.objects.select_related(
        'author'
    ).filter(post__id=post_id)
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(Category.objects.values(
        'title', 'description', 'id'
    ), slug=category_slug, is_published=True)
    post_list = post_object(category_slug).annotate(
        comment_count=Count('Comments')
    ).order_by('-pub_date')
    paginator = Paginator(post_list, PAGE_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'category': category}
    return render(request, template, context)


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        object = self.get_object()
        return redirect('blog:post_detail', object.pk)


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


def profile(request, username):
    template = 'blog/profile.html'
    profile = get_object_or_404(User, username=username)
    post_list = Post.objects.select_related(
        'location', 'category', 'author',
    ).filter(author__username=username).annotate(
        comment_count=Count('Comments')
    ).order_by('-pub_date')
    paginator = Paginator(post_list, PAGE_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'profile': profile}
    return render(request, template, context)


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
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse('blog:post_detail', kwargs={'post_id': post_id})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        Comments = form.save(commit=False)
        Comments.author = request.user
        Comments.post = post
        Comments.save()
    return redirect('blog:post_detail', post_id)


class CommentEditView(OnlyAuthorMixin, CommentMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(OnlyAuthorMixin, CommentMixin, DeleteView):
    pass
