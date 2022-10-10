def incr_likes_count(sender, instance, created, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F
    from utils.redis_helper import RedisHelper

    if not created:
        return

    model_class = instance.content_type.model_class()
    # comments' like_count is similar
    if model_class != Tweet:
        return

    # update is an atom operation
    # SQL query: UPDATE likes_count = likes_count + 1 FROM tweets_table WHERE id=instance.object_id
    Tweet.objects.filter(id=instance.object_id).update(likes_count=F('likes_count') + 1)
    RedisHelper.incr_count(instance.content_object, 'likes_count')
    # method 1
    # here must use F

    # method 2
    # tweet = instance.content_object
    # tweet.likes_count = F('likes_count') + 1
    # tweet.save()


def decr_likes_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F
    from utils.redis_helper import RedisHelper

    model_class = instance.content_type.model_class()
    if model_class != Tweet:
        return

    Tweet.objects.filter(id=instance.object_id).update(likes_count=F('likes_count') - 1)
    RedisHelper.decr_count(instance.content_object, 'likes_count')
