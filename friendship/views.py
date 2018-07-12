from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.models import User

from friendship.templatetags.friendshiptags import register

try:
    from django.contrib.auth import get_user_model

    user_model = get_user_model()
except ImportError:
    from django.contrib.auth.models import User

    user_model = User

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from friendship.exceptions import AlreadyExistsError
from friendship.models import Friend, FriendshipRequest

get_friendship_context_object_name = lambda: getattr(settings, 'FRIENDSHIP_CONTEXT_OBJECT_NAME', 'user')
get_friendship_context_object_list_name = lambda: getattr(settings, 'FRIENDSHIP_CONTEXT_OBJECT_LIST_NAME', 'users')


@login_required
def view_friends(request, username, template_name='friendship/friend/user_list.html'):
    """ View the friends of a user """
    myfriends = Friend.objects.filter( \
        Q(from_user=request.user) | \
        Q(to_user=request.user))
    user = request.user
    return render(request, template_name, {
        'myfriends': myfriends, 'user': user
    })


@login_required
def friendship_add_friend(request, to_username, template_name='friendship/friend/add.html'):
    """ Create a FriendshipRequest """
    ctx = {'to_username': to_username}

    if request.method == 'GET':
        to_user = User.objects.get(username=to_username)
        from_user = request.user
        rqst=FriendshipRequest.objects.create(from_user=from_user, to_user=to_user)
        rqst.save()
        return redirect('friendship:friendship_view_users')

    return render(request, template_name, ctx)


@login_required
def friendship_accept(request, friend):
    """ Accept a friendship request """
    if request.method == 'GET':
        user = User.objects.get(username=friend)
        f_request = Friend.objects.create(from_user=user, to_user=request.user)
        f_request.save()
        FriendshipRequest.objects.get(from_user=user, to_user=request.user, rejected__isnull=True).mark_viewed()
        return redirect('friendship:friendship_view_friends', username=request.user.username)

    return redirect('friendship:friendship_request_list')


@login_required
def friendship_reject(request, friend):
    """ Reject a friendship request """
    if request.method == 'GET':
        user = User.objects.get(username=friend)
        f_request = FriendshipRequest.objects.get(to_user=request.user, from_user=user)
        f_request.reject()
        return redirect('friendship:friendship_request_list')

    return redirect('friendship:friendship_request_list')


@login_required
def friendship_cancel(request, friend):
    """ Cancel a previously created friendship_request_id """

    if request.method == 'GET':
        getid = User.objects.get(username = friend)
        Friend.objects.filter(\
            Q(from_user=request.user, to_user_id=getid.id) |\
            Q(from_user_id=getid.id, to_user=request.user) \
        ).delete()
        FriendshipRequest.objects.filter( \
            Q(from_user=request.user, to_user_id=getid.id) | \
            Q(from_user_id=getid.id, to_user=request.user) \
            ).delete()

        return redirect('friendship:friendship_view_friends', username=request.user)

    return redirect('friendship:friendship_view_friends', username=request.user)


@login_required
def friendship_request_list(request, template_name='friendship/friend/requests_list.html'):
    """ View unread and read friendship requests """
    requestme = FriendshipRequest.objects.filter( \
        Q(to_user=request.user, viewed__isnull=True, rejected__isnull=True)).values_list('from_user', flat=True)
    u = request.user
    users = User.objects.filter(id__in=requestme)
    return render(request, template_name, {'users': users, 'u': u})


@login_required
def friendship_request_list_rejected(request, template_name='friendship/friend/requests_list.html'):
    """ View rejected friendship requests """
    # friendship_requests = Friend.objects.rejected_requests(request.user)
    friendship_requests = FriendshipRequest.objects.filter(rejected__isnull=False)

    return render(request, template_name, {'requests': friendship_requests})


@login_required
def friendship_requests_detail(request, friendship_request_id, template_name='friendship/friend/request.html'):
    """ View a particular friendship request """
    f_request = get_object_or_404(FriendshipRequest, id=friendship_request_id)

    return render(request, template_name, {'friendship_request': f_request})


@login_required
def all_users(request):
    already = Friend.objects.filter( \
        Q(from_user=request.user) | \
        Q(to_user=request.user)).values_list('to_user', flat=True)

    requestme = FriendshipRequest.objects.filter( \
        Q(to_user=request.user, rejected__isnull=True)).values_list('from_user', flat=True)

    users = User.objects.exclude( \
        Q(id__in=already) | \
        Q(id=request.user.id) | \
        Q(username="admin") | \
        Q(id__in=requestme)).order_by("username")

    requestbyme = FriendshipRequest.objects.filter( \
        Q(from_user=request.user, viewed__isnull=True)).values_list('to_user', flat=True)

    requestbymeuser = User.objects.filter(id__in=requestbyme)

    return render(request, template_name='friendship/friend/add.html', context={'users': users, 'requestbymeuser': requestbymeuser })


'''@register.filter
def mutual(request,  fromuser):
    count = 0
    touserfriend1 = Friend.objects.filter(from_user=request.user).values_list('to_user', flat=True)
    touserfriend2 = Friend.objects.filter(to_user=request.user).values_list('from_user', flat=True)
    total_friend1 = list(touserfriend1).append(list(touserfriend2))

    fromuserfriend1 = Friend.objects.filter(from_user=fromuser).values_list('to_user', flat=True)
    fromuserfriend2 = Friend.objects.filter(to_user=fromuser).values_list('from_user', flat=True)
    total_friend2 = list(fromuserfriend1).append(list(fromuserfriend2))

    for x in total_friend1:
        for y in total_friend2:
            if x == y:
                count = count+1
    return count'''
