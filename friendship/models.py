from __future__ import unicode_literals
from django.db import models
from django.conf import settings
from django.db.models import Q
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from friendship.exceptions import AlreadyExistsError, AlreadyFriendsError
from friendship.signals import (
    friendship_request_created, friendship_request_rejected,
    friendship_request_canceled,
    friendship_request_viewed, friendship_request_accepted,
    friendship_removed)

@python_2_unicode_compatible
class FriendshipRequest(models.Model):
    """ Model to represent friendship requests """
    from_user = models.ForeignKey(User, related_name='friendship_requests_sent', on_delete=models.CASCADE, unique=False)
    to_user = models.ForeignKey(User, related_name='friendship_requests_received', on_delete=models.CASCADE, unique=False)

    message = models.TextField(_('Message'), blank=True)

    created = models.DateTimeField(default=timezone.now)
    rejected = models.DateTimeField(blank=True, null=True)
    viewed = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _('Friendship Request')
        verbose_name_plural = _('Friendship Requests')
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return "%s" % self.from_user.username

    def accept(self):
        """ Accept this friendship request """
        relation1 = Friend.objects.create(
            from_user=self.from_user,
            to_user=self.to_user
        )

        relation2 = Friend.objects.create(
            from_user=self.to_user,
            to_user=self.from_user
        )

        friendship_request_accepted.send(
            sender=self,
            from_user=self.from_user,
            to_user=self.to_user
        )

        self.delete()

        # Delete any reverse requests
        FriendshipRequest.objects.filter(
            from_user=self.to_user,
            to_user=self.from_user
        ).delete()

        return True

    def reject(self):
        """ reject this friendship request """
        self.rejected = timezone.now()
        self.save()
        friendship_request_rejected.send(sender=self)


    def cancel(self):
        """ cancel this friendship request """
        self.delete()
        friendship_request_canceled.send(sender=self)
        return True

    def mark_viewed(self):
        self.viewed = timezone.now()
        friendship_request_viewed.send(sender=self)
        self.save()
        return True


@python_2_unicode_compatible
class Friend(models.Model):
    """ Model to represent Friendships """
    to_user = models.ForeignKey(User, related_name='friends', on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, related_name='_unused_friend_relation', on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _('Friend')
        verbose_name_plural = _('Friends')
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return "User #%s is friends with #%s" % (self.to_user.username, self.from_user.username)

    def mutual(self, request):
        count = 0
        touserfriend1 = Friend.objects.filter(from_user=request.user).values_list('to_user', flat=True)
        touserfriend2 = Friend.objects.filter(to_user=request.user).values_list('from_user', flat=True)
        total_friend1 = list(touserfriend1).append(list(touserfriend2))

        fromuserfriend1 = Friend.objects.filter(from_user=self).values_list('to_user', flat=True)
        fromuserfriend2 = Friend.objects.filter(to_user=self).values_list('from_user', flat=True)
        total_friend2 = list(fromuserfriend1).append(list(fromuserfriend2))

        for x in total_friend1:
            for y in total_friend2:
                if x == y:
                    count = count+1
        return count

    def save(self, *args, **kwargs):
        # Ensure users can't be friends with themselves
        if self.to_user == self.from_user:
            raise ValidationError("Users cannot be friends with themselves.")
        super(Friend, self).save(*args, **kwargs)


