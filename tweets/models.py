from django.db import models
from django.contrib.auth.models import User
from utils.time_helpers import utc_now


# Create your models here.
class Tweet(models.Model):
    # thw author of the post
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        ordering = ('user', '-created_at')

    @property
    def hours_to_now(self):
        # datetime.now  no time zone in it
        return (utc_now() - self.created_at).seconds // 3600

    def __str__(self):
        # what is displayed when executing  print(tweet instance)
        return f'{self.created_at} {self.user}: {self.content}'
