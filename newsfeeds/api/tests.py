# from newsfeeds.models import NewsFeed
from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase


NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'


class NewsFeedApiTests(TestCase):

    def setUp(self):

        self.anonymous_client = APIClient()

        self.qwerty = self.create_user('qwerty', 'qwerty@twitter.com')
        self.qwerty_client = APIClient()
        self.qwerty_client.force_authenticate(self.qwerty)

        self.asdfgh = self.create_user('asdfgh', 'qwerty@twitter.com')
        self.asdfgh_client = APIClient()
        self.asdfgh_client.force_authenticate(self.asdfgh)

        # create followings and followers for asdfgh
        for i in range(2):
            follower = self.create_user('asdfgh_follower{}'.format(i), str(i) + 'user1@twitter.com')
            Friendship.objects.create(from_user=follower, to_user=self.asdfgh)
        for i in range(3):
            following = self.create_user('asdfgh_following{}'.format(i), str(i) + 'user2@twitter.com')
            Friendship.objects.create(from_user=self.asdfgh, to_user=following)

    def test_list(self):
        # 需要登录
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 403)
        # 不能用 post
        response = self.qwerty_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 405)
        # 一开始啥都没有
        response = self.qwerty_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['newsfeeds']), 0)
        # 自己发的信息是可以看到的
        self.qwerty_client.post(POST_TWEETS_URL, {'content': 'Hello World'})
        response = self.qwerty_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 1)
        # 关注之后可以看到别人发的
        self.qwerty_client.post(FOLLOW_URL.format(self.asdfgh.id))
        response = self.asdfgh_client.post(POST_TWEETS_URL, {
            'content': 'Hello Twitter',
        })
        posted_tweet_id = response.data['id']
        response = self.qwerty_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 2)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['id'], posted_tweet_id)
