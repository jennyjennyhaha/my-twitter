from newsfeeds.services import NewsFeedService
from testing.testcases import TestCase
from twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_client import RedisClient
from newsfeeds.tasks import fanout_newsfeeds_main_task
from newsfeeds.models import NewsFeed


class NewsFeedServiceTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.qwerty = self.create_user('qwerty', 'qwerty@twitter.com')
        self.asdfgh = self.create_user('asdfgh', 'asdfgh@twitter.com')

    def test_get_user_newsfeeds(self):
        newsfeed_ids = []
        for i in range(3):
            tweet = self.create_tweet(self.asdfgh)
            newsfeed = self.create_newsfeed(self.qwerty, tweet)
            newsfeed_ids.append(newsfeed.id)
        newsfeed_ids = newsfeed_ids[::-1]

        # cache miss
        newsfeeds = NewsFeedService.get_cached_newsfeeds(self.qwerty.id)
        self.assertEqual([f.id for f in newsfeeds], newsfeed_ids)

        # cache hit
        newsfeeds = NewsFeedService.get_cached_newsfeeds(self.qwerty.id)
        self.assertEqual([f.id for f in newsfeeds], newsfeed_ids)

        # cache updated
        tweet = self.create_tweet(self.qwerty)
        new_newsfeed = self.create_newsfeed(self.qwerty, tweet)
        newsfeeds = NewsFeedService.get_cached_newsfeeds(self.qwerty.id)
        newsfeed_ids.insert(0, new_newsfeed.id)
        self.assertEqual([f.id for f in newsfeeds], newsfeed_ids)

    def test_create_new_newsfeed_before_get_cached_newsfeeds(self):
        feed1 = self.create_newsfeed(self.qwerty, self.create_tweet(self.qwerty))

        RedisClient.clear()
        conn = RedisClient.get_connection()

        key = USER_NEWSFEEDS_PATTERN.format(user_id=self.qwerty.id)
        self.assertEqual(conn.exists(key), False)
        feed2 = self.create_newsfeed(self.qwerty, self.create_tweet(self.qwerty))
        self.assertEqual(conn.exists(key), True)

        feeds = NewsFeedService.get_cached_newsfeeds(self.qwerty.id)
        self.assertEqual([f.id for f in feeds], [feed2.id, feed1.id])


class NewsFeedTaskTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.qwerty = self.create_user('qwerty', 'qwerty@twitter.com')
        self.asdfgh = self.create_user('asdfgh', 'asdfgh@twitter.com')

    def test_fanout_main_task(self):
        tweet = self.create_tweet(self.qwerty, 'tweet 1')
        self.create_friendship(self.asdfgh, self.qwerty)
        msg = fanout_newsfeeds_main_task(tweet.id, self.qwerty.id)
        self.assertEqual(msg, '1 newsfeeds going to fanout, 1 batches created.')
        self.assertEqual(1 + 1, NewsFeed.objects.count())
        cached_list = NewsFeedService.get_cached_newsfeeds(self.qwerty.id)
        self.assertEqual(len(cached_list), 1)

        for i in range(2):
            user = self.create_user('user{}'.format(i), str(i) + 'user@twitter.com')
            self.create_friendship(user, self.qwerty)
        tweet = self.create_tweet(self.qwerty, 'tweet 2')
        msg = fanout_newsfeeds_main_task(tweet.id, self.qwerty.id)
        self.assertEqual(msg, '3 newsfeeds going to fanout, 1 batches created.')
        self.assertEqual(4 + 2, NewsFeed.objects.count())
        cached_list = NewsFeedService.get_cached_newsfeeds(self.qwerty.id)
        self.assertEqual(len(cached_list), 2)

        user = self.create_user('another user', 'another@twitter.com')
        self.create_friendship(user, self.qwerty)
        tweet = self.create_tweet(self.qwerty, 'tweet 3')
        msg = fanout_newsfeeds_main_task(tweet.id, self.qwerty.id)
        self.assertEqual(msg, '4 newsfeeds going to fanout, 2 batches created.')
        self.assertEqual(8 + 3, NewsFeed.objects.count())
        cached_list = NewsFeedService.get_cached_newsfeeds(self.qwerty.id)
        self.assertEqual(len(cached_list), 3)
        cached_list = NewsFeedService.get_cached_newsfeeds(self.asdfgh.id)
        self.assertEqual(len(cached_list), 3)
