from django.test import TestCase as DjangoTestCase
from django.contrib.auth.models import User
from tweets.models import Tweet
from comments.models import Comment


class TestCase(DjangoTestCase):
    def create_user(self, username, email, password=None):
        if password is None:
            password = 'generic password'
        # cannot be User.objects.create()
        # since password needs encryption and username and email needs some normalize
        return User.objects.create_user(username, email, password)

    def create_tweet(self, user, content=None):
        if content is None:
            content = 'default tweet content'
        return Tweet.objects.create(user=user, content=content)

    def create_comment(self, user, tweet, content=None):
        if content is None:
            content = 'default comment content'
        return Comment.objects.create(user=user, tweet=tweet, content=content)
