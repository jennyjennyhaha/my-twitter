from django.test import TestCase as DjangoTestCase
from django.contrib.auth.models import User
from tweets.models import Tweet
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.core.cache import caches
from likes.models import Like
from rest_framework.test import APIClient
from newsfeeds.models import NewsFeed


class TestCase(DjangoTestCase):

    def clear_cache(self):
        caches['testing'].clear()

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

    def create_like(self, user, target):
        instance, _ = Like.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
            user=user,
        )
        return instance

    def create_user_and_client(self, *args, **kwargs):
        user = self.create_user(*args, **kwargs)
        client = APIClient()
        client.force_authenticate(user)
        return user, client

    def create_newsfeed(self, user, tweet):
        return NewsFeed.objects.create(user=user, tweet=tweet)



