from django.urls import path
from home import views
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from home.models import Post, Comment, LikeDislike


app_name = 'home'
urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('comments/<int:pk>/', views.comments, name='comments'),
    path('write_comments/<int:pk>', views.write_comments, name='write_comments'),
    path('delete_comment/<int:pk>', views.delete_comment, name='delete_comment'),
    path('delete_post/<int:pk>', views.delete_post, name='delete_post'),
    path('post_by_me/', views.post_by_me, name='post_by_me'),
    url(r'^post/(?P<pk>\d+)/like/$',
        login_required(views.VotesView.as_view(model=Post, vote_type=LikeDislike.LIKE)),
        name='post_like'),
    url(r'^post/(?P<pk>\d+)/dislike/$',
        login_required(views.VotesView.as_view(model=Post, vote_type=LikeDislike.DISLIKE)),
        name='post_dislike'),
    url(r'^comment/(?P<pk>\d+)/like/$',
        login_required(views.VotesView.as_view(model=Comment, vote_type=LikeDislike.LIKE)),
        name='comment_like'),
    url(r'^comment/(?P<pk>\d+)/dislike/$',
        login_required(views.VotesView.as_view(model=Comment, vote_type=LikeDislike.DISLIKE)),
        name='comment_dislike'),
]