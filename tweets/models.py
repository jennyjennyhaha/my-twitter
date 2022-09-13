from django.db import models
from django.contrib.auth.models import User
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

    # at first at the time of model creation, there is no such class
    class Meta:
        index_together = (('user', 'created_at'),)
        ordering = ('user', '-created_at')

    @property
    def hours_to_now(self):
        # datetime.now  no time zone in it, we need to add the time zone info of utc
        return (utc_now() - self.created_at).seconds // 3600

    def __str__(self):
        # what is displayed when executing  print(tweet instance)
        return f'{self.created_at} {self.user}: {self.content}'
