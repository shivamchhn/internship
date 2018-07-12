from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import Sum
from django.contrib.contenttypes.fields import GenericRelation


class LikeDislikeManager(models.Manager):
    use_for_related_fields = True

    def likes(self):
        # We take the queryset with records greater than 0
        return self.get_queryset().filter(vote__gt=0)

    def dislikes(self):
        # We take the queryset with records less than 0
        return self.get_queryset().filter(vote__lt=0)

    def sum_rating(self):
        # We take the total rating
        return self.get_queryset().aggregate(Sum('vote')).get('vote__sum') or 0

    def post(self):
        return self.get_queryset().filter(content_type__model='post').order_by('-post__pub_date')

    def comments(self):
        return self.get_queryset().filter(content_type__model='comment').order_by('-comment__pub_date')


class LikeDislike(models.Model):
    LIKE = 1
    DISLIKE = -1

    VOTES = (
        (DISLIKE, 'Dislike'),
        (LIKE, 'Like')
    )

    vote = models.SmallIntegerField(choices=VOTES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    objects = LikeDislikeManager()


class Post(models.Model):
    votes = GenericRelation(LikeDislike, related_query_name='post')
    post = models.CharField(max_length=1000)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='profile_image', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.post

    @property
    def cnt(self):
        return self.like_set.all().count()

    @property
    def total_comment(self):
        return self.comment_set.all().count()


class Comment(models.Model):
    votes = GenericRelation(LikeDislike, related_query_name='comment')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post.post


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} likes \'{self.post.post}\''


