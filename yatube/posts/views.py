from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from yatube.settings import PAGE_SIZE

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


@cache_page(20)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'page': page, 'group': group})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    following = False
    if request.user.is_anonymous is True:
        pass
    elif request.user.is_authenticated is True:
        following = request.user.follower.filter(author=author).exists()
    paginator = Paginator(post_list, PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'author': author,
        'following': following,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    author = post.author
    form = CommentForm(request.POST or None)
    following = False
    if request.user.is_anonymous is True:
        pass
    elif request.user.follower.filter(author=author):
        following = True
    context = {
        'author': author,
        'post': post,
        'following': following,
        'form': form
    }
    return render(request, 'post.html', context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new.html', {'form': form, 'func': 'new_post'})


@login_required
def post_edit(request, username, post_id):
    if request.user.username == username:
        post = get_object_or_404(Post, author__username=username, pk=post_id)
        form = PostForm(
            request.POST or None, files=request.FILES or None, instance=post
        )
        if form.is_valid():
            post.save()
            return redirect('post', username=username, post_id=post_id)

        return render(request, 'new.html',
                      {'form': form, 'func': 'post_edit', 'post': post})
    return redirect('post', username=username, post_id=post_id)


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(
            Post, author__username=username, pk=post_id
        )
        comment.save()
        return redirect('post', username=username, post_id=post_id)
    return render(request, 'comments.html', {'form': form})


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page})


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    user = request.user
    if user != author:
        Follow.objects.get_or_create(
            user=user,
            author=author)
    return redirect('follow_index')


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    followship = Follow.objects.get(
        user=request.user,
        author=author)
    followship.delete()
    return redirect('index')


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
