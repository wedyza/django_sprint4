from django.shortcuts import render, get_object_or_404, redirect
# Create your views here.
from .models import Post, Category, Comment
from django.http import Http404
from django.contrib.auth import get_user_model
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import PostForm, UserForm, CommentForm
from django.views import generic
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
User = get_user_model()


def index(request):
    template = 'blog/index.html'
    posts = Post.objects.select_related('category').filter(is_published=True) \
        .filter(category__is_published=True) \
        .filter(pub_date__date__lt=timezone.now()).order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'blog/detail.html'
    post = get_object_or_404(Post, pk=post_id)
    if not post.is_published \
        or post.pub_date > timezone.now() \
        or not post \
            or not post.category.is_published:
        raise Http404
    comments = Comment.objects.filter(post_id=post_id)
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, template, context)


def category_posts(request, category_slug):
    category = Category.objects.filter(slug=category_slug).first()
    if not category.is_published:
        raise Http404

    posts = Post.objects.select_related('category').filter(is_published=True) \
        .filter(category__slug=category_slug) \
        .filter(pub_date__date__lt=timezone.now()).order_by('-pub_date')
    template = 'blog/category.html'
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'category': category
    }
    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-pub_date')
    template_name = 'blog/profile.html'
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': user,
        'page_obj': page_obj
    }

    return render(request, template_name, context)


def edit_profile(request):
    user = request.user
    form = UserForm(user)
    context = {
        'form': form
    }
    template_name = 'blog/user.html'
    return render(request, template_name, context)


class UserUpdate(UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostBase(LoginRequiredMixin):
    model = Post
    success_url = reverse_lazy('blog:profile')

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user)


class CreatePost(PostBase, generic.CreateView):
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        new_post = form.save(commit=False)
        new_post.author = self.request.user
        new_post.save()
        return super().form_valid(form)


class UpdatePost(PostBase, generic.UpdateView):
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class DeletePost(PostBase, generic.DeleteView):
    template_name = 'blog/create.html'


@login_required
def post_comment(request, post_id):
    form = CommentForm(request.POST)
    post = get_object_or_404(Post, post_id)
    if request.user is None or post is None:
        return Http404
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()

    return redirect('blog:post_detail', post_id)


class CommentBase(LoginRequiredMixin):
    model = Comment

    def get_success_url(self):
        comment = self.get_object()
        return reverse(
            'blog:post_detail', kwargs={'post_id': comment.post.id}
        ) + '#comments'

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user)


class UpdateComment(CommentBase, generic.UpdateView):
    form_class = CommentForm
    template_name = 'blog/comment.html'


class DeleteComment(CommentBase, generic.DeleteView):
    template_name = 'blog/comment.html'
