from utils.listeners import invalidate_object_cache


def incr_comments_count(sender, instance, created, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F
    from utils.redis_helper import RedisHelper

    if not created:
        return

    # handle new comment
    Tweet.objects.filter(id=instance.tweet_id).update(comments_count=F('comments_count') + 1)
    RedisHelper.incr_count(instance.tweet, 'comments_count')
    # invalidate_object_cache(sender=Tweet, instance=instance.tweet)
    # method 1
    # here must use F

    # method 2
    # tweet = instance.content_object
    # tweet.likes_count = F('likes_count') + 1
    # tweet.save()


def decr_comments_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F
    from utils.redis_helper import RedisHelper

    # handle comment deletion
    Tweet.objects.filter(id=instance.tweet_id).update(comments_count=F('comments_count') - 1)
    RedisHelper.decr_count(instance.tweet, 'comments_count')
    # invalidate_object_cache(sender=Tweet, instance=instance.tweet)
