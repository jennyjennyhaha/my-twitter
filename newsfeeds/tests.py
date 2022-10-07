from newsfeeds.services import NewsFeedService
from testing.testcases import TestCase
from twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_client import RedisClient


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
