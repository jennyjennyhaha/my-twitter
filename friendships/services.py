from django.conf import settings
from django.core.cache import caches
from friendships.models import Friendship
from twitter.cache import FOLLOWINGS_PATTERN

cache = caches['testing'] if settings.TESTING else caches['default']


# follower number is usually very high, and usually updated frequently, so not
# suitable for cache
class FriendshipService(object):
    @classmethod
    def get_followers(cls, user):
        friendships = Friendship.objects.filter(
            to_user=user,
        ).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]

    # wrong way one
    # this way will lead to  N + 1 Queries problem
    # wherein filter all friendships takes one Query
    # and for loop every friendship to get from_user takes N Queries
    # friendships = Friendship.objects.filter(to_user=user)
    # return [friendship.from_user for friendship in friendships]

    # wrong way two
    # use JOIN operation to join friendship table and user table in attribute from_user
    #  join operation is forbidden in mass user web scenario due to being too slow
    # friendships = Friendship.objects.filter(
    #     to_user=user
    # ).select_related('from_user')
    # return [friendship.from_user for friendship in friendships]

    # another right way: manually filter id，inquery with IN Query
    # friendships = Friendship.objects.filter(to_user=user)
    # follower_ids = [friendship.from_user_id for friendship in friendships]
    # followers = User.objects.filter(id__in=follower_ids)

    # following uses cache
    @classmethod
    def get_following_user_id_set(cls, from_user_id):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        user_id_set = cache.get(key)
        if user_id_set is not None:
            return user_id_set

        friendships = Friendship.objects.filter(from_user_id=from_user_id)
        user_id_set = set([
            fs.to_user_id
            for fs in friendships
        ])
        cache.set(key, user_id_set)
        return user_id_set

    @classmethod
    def invalidate_following_cache(cls, from_user_id):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        cache.delete(key)


