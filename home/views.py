import json

from django.http import HttpResponse
from django.views import View
from django.contrib.contenttypes.models import ContentType
from django.views.generic import TemplateView
from home.forms import HomeForm, CommentForm
from django.shortcuts import redirect, render
from home.models import Post, Comment, Like, LikeDislike
from friendship.models import Friend
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django_ajax.decorators import ajax
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

@method_decorator(login_required, name='dispatch')
class Home(TemplateView):
    template_name = 'home/home.html'

    def get(self, request):
        form = HomeForm()

        friends_and_user1 = Friend.objects.filter(\
            Q(from_user=request.user)).values_list('to_user', flat=True)

        friends_and_user2 = Friend.objects.filter( \
            Q(to_user=request.user)).values_list('from_user', flat=True)

        posts = Post.objects.filter( \
            Q(user_id__in=friends_and_user1) | \
            Q(user_id__in=friends_and_user2) | \
            Q(user=request.user)).order_by('-created')
        users = User.objects.exclude(id=request.user.id)[1:]
        args = {'form': form, 'posts': posts, 'users': users}
        return render(request, self.template_name, args)

    def post(self, request):
        form = HomeForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            text = form.cleaned_data['post']
            form = HomeForm()
            return redirect('home:home')
        args = {'form': form, 'text': form.cleaned_data['post']}
        return render(request, self.template_name, args)


@login_required()
def comments(request, pk=None):
    template_name = 'home/all_comments.html'
    cmnt = Comment.objects.filter(post_id=pk).order_by('-created')
    post = Post.objects.get(pk=pk)
    count = Comment.objects.filter(post_id=pk).count()
    context = {'cmnt': cmnt, 'post': post, 'count': count}
    return render(request, template_name, context)


# def already_liked_post(user, post):
#     return Like.objects.filter(user=user, post=post).exists()


# @ajax
# def likes(request, pk=None):
#     if request.method == "POST":
#         post = Post.objects.get(id=pk)
#
#         if not already_liked_post(request.user, post):
#             Like.objects.create(user=request.user, post=post)
#         else:
#             Like.objects.filter(user=request.user, post=post).delete()
#
#         likecount = Like.objects.filter(post=post).count()
#         return {'likecount': likecount}
#     else:
#         post = Post.objects.get(id=pk)
#
#         if not already_liked_post(request.user, post):
#             Like.objects.create(user=request.user, post=post)
#         else:
#             Like.objects.filter(user=request.user, post=post).delete()
#
#         likecount = Like.objects.filter(post=post).count()
#         return {'likecount': likecount}
#
#
# class Write_comments(TemplateView):
#     template_name = 'home/write_comments.html'
#
#     def get(self, request):
#         form = CommentForm()
#
#         cmnt = User.comment_set.filter(id=request.user.id)
#         args = {'form': form, 'cmnt': cmnt, 'user': request.user}
#         return render(request, self.template_name, args)
#
#     def post(self, request):
#         form = CommentForm(request.POST)
#         if form.is_valid():
#
#
#             text = form.cleaned_data['comment']
#             form = CommentForm()
#             return redirect('home:write_comment')
#         args = {'form': form}
#         return render(request, self.template_name, args)


@login_required()
def write_comments(request, pk=None):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = Post.objects.get(id=pk)
            comment.save()
            return redirect('home:comments', pk=pk)
        else:
            return redirect('home:write_comments')

    else:
        form = CommentForm()

        cmnt = Comment.objects.filter(post_id=pk, user_id=request.user.id).order_by('-created')
        post = Post.objects.get(pk=pk)
        args = {'form': form, 'cmnt': cmnt, 'post': post}
        return render(request, 'home/write_comments.html', args)


@login_required
def delete_comment(request, pk=None):
    if request.method == 'POST':
        cmnt = Comment.objects.get(pk=pk)
        post_id = cmnt.post_id
        cmnt.delete()
        return redirect('home:comments', pk=post_id)
    else:
        cmnt = Comment.objects.get(pk=pk)
        post_id = cmnt.post_id
        cmnt.delete()
        return redirect('home:write_comments', pk=post_id)


@login_required
def post_by_me(request):
    posts = request.user.post_set.all().order_by('-created')
    context = {'posts': posts}
    return render(request, 'home/post_by_me.html', context)


# @login_required
# def post_liked_by_me(request):
#     likes = Like.objects.filter(user=request.user).order_by('-timestamp')
#
#     context = {'likes': likes}
#     return render(request, 'home/post_liked_by_me.html', context)


@login_required
def delete_post(request, pk=None):
    print("bye")
    pst = Post.objects.filter(pk=pk)
    print(pst)
    pst.delete()
    print("bye3")
    return redirect('home:post_by_me')


class VotesView(View):
    model = None  # Data Model - Articles or Comments
    vote_type = None  # Vote type Like/Dislike

    def post(self, request, pk):
        obj = self.model.objects.get(pk=pk)
        # GenericForeignKey does not support get_or_create
        try:
            likedislike = LikeDislike.objects.get(content_type=ContentType.objects.get_for_model(obj), object_id=obj.id,
                                                  user=request.user)
            if likedislike.vote is not self.vote_type:
                likedislike.vote = self.vote_type
                likedislike.save(update_fields=['vote'])
                result = True
            else:
                likedislike.delete()
                result = False
        except LikeDislike.DoesNotExist:
            obj.votes.create(user=request.user, vote=self.vote_type)
            result = True

        return HttpResponse(
            json.dumps({
                "result": result,
                "like_count": obj.votes.likes().count(),
                "dislike_count": obj.votes.dislikes().count(),
                "sum_rating": obj.votes.sum_rating()
            }),
            content_type="application/json"
        )