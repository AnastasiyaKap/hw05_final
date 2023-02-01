from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CommentForm, PostForm
from .models import Comment, Group, Follow, Post, User
from .utils import get_page


def index(request):
    context = get_page(Post.objects.select_related('group'), request)
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    context = {
        'group': group
    }
    context.update(get_page(group.posts.all(), request))
    return render(request, 'posts/group_list.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post_id=post.pk)
    context = {
        'post': post,
        'form': CommentForm(),
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=post.author)


def profile(request, username):
    following = False
    author = get_object_or_404(User, username=username)
    if request.user.is_authenticated:
        following = author.following.filter(user=request.user).exists()
    context = {
        'author': author,
        'following': following
    }
    context.update(get_page(author.posts.all(), request))
    return render(request, 'posts/profile.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    follower_user = request.user
    following_user = Follow.objects.filter(user=follower_user).values('author')
    context = {
        'following_user': following_user,
    }
    context.update(get_page(Post.objects.filter(author__in=following_user),
                   request))
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    following_user = request.user
    if author != following_user:
        if Follow.objects.get_or_create(user=following_user, author=author):
            return redirect('posts:profile', username=username)
    else:
        return redirect('posts:index')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if Follow.objects.filter(user=user, author=author).exists():
        Follow.objects.filter(user=user, author=author).delete()
        return redirect('posts:profile', username=username)
    return redirect('posts:profile', username=username)
