from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save, pre_delete
from likes.models import Like
from tweets.constants import TweetPhotoStatus, TWEET_PHOTO_STATUS_CHOICES
from tweets.listeners import push_tweet_to_cache
from utils.listeners import invalidate_object_cache
from utils.memcached_helper import MemcachedHelper
from utils.time_helpers import utc_now


# Create your models here.
# what we will do when the user send a tweet
class Tweet(models.Model):
    # thw author of the post
    # user and tweets: one to many, so use foreignKey to implement
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        # help_test='the author of this tweet',
    )
    # save the tweets with any length
    content = models.CharField(max_length=255)
    # save the posting time of the tweet
    created_at = models.DateTimeField(auto_now_add=True)

    # newly added field has to be null=True, or default = 0 will traverse every old table to set the value
    # and slow down the migration and lock the table. The user might not be able to create new tweets.
    likes_count = models.IntegerField(default=0, null=True)
    comments_count = models.IntegerField(default=0, null=True)

    # at first at the time of model creation, there is no such class
    class Meta:
        index_together = (('user', 'created_at'),)
        ordering = ('user', '-created_at')

    def __str__(self):
        # what is displayed when executing  print(tweet instance)
        return f'{self.created_at} {self.user}: {self.content}'

    @property
    def hours_to_now(self):
        # datetime.now  no time zone in it, we need to add the time zone info of utc
        return (utc_now() - self.created_at).seconds // 3600

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')

    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)


class TweetPhoto(models.Model):
    # photo is under which Tweet
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)

    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    # file
    file = models.FileField()
    order = models.IntegerField(default=0)

    # status, store with integer, so that the change of its meaning is convenient
    status = models.IntegerField(
        default=TweetPhotoStatus.PENDING,
        choices=TWEET_PHOTO_STATUS_CHOICES,
    )

    # soft delete for async
    has_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('user', 'created_at'),
            ('has_deleted', 'created_at'),
            ('status', 'created_at'), # the above will be used by the examiners
            ('tweet', 'order'), # ordinary user will use it
        )

    def __str__(self):
        return f'{self.tweet_id}: {self.file}'


# hook up with listeners to invalidate cache
post_save.connect(invalidate_object_cache, sender=Tweet)
pre_delete.connect(invalidate_object_cache, sender=Tweet)
post_save.connect(push_tweet_to_cache, sender=Tweet)
