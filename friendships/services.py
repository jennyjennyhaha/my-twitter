from friendships.models import Friendship


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
