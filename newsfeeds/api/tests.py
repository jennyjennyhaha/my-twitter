from django.conf import settings
from friendships.models import Friendship
from newsfeeds.models import NewsFeed
from newsfeeds.services import NewsFeedService
from rest_framework.test import APIClient
from testing.testcases import TestCase
from utils.paginations import EndlessPagination


NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'


class NewsFeedApiTests(TestCase):

    def setUp(self):
        self.clear_cache()
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
        # need log in
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 403)
        # cannot use post
        response = self.qwerty_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 405)
        # there is nothing
        response = self.qwerty_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)
        # can see own tweet
        self.qwerty_client.post(POST_TWEETS_URL, {'content': 'Hello World'})
        response = self.qwerty_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['results']), 1)
        # can see other's after following
        self.qwerty_client.post(FOLLOW_URL.format(self.asdfgh.id))
        response = self.asdfgh_client.post(POST_TWEETS_URL, {
            'content': 'Hello Twitter',
        })
        posted_tweet_id = response.data['id']
        response = self.qwerty_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['tweet']['id'], posted_tweet_id)

    def test_pagination(self):
        page_size = EndlessPagination.page_size
        followed_user = self.create_user('followed', 'followed@twitter.com')
        newsfeeds = []
        for i in range(page_size * 2):
            tweet = self.create_tweet(followed_user)
            newsfeed = self.create_newsfeed(user=self.qwerty, tweet=tweet)
            newsfeeds.append(newsfeed)

        newsfeeds = newsfeeds[::-1]

        # pull the first page
        response = self.qwerty_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.data['has_next_page'], True)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], newsfeeds[0].id)
        self.assertEqual(response.data['results'][1]['id'], newsfeeds[1].id)
        self.assertEqual(
            response.data['results'][page_size - 1]['id'],
            newsfeeds[page_size - 1].id,
        )

        # pull the second page
        response = self.qwerty_client.get(
            NEWSFEEDS_URL,
            {'created_at__lt': newsfeeds[page_size - 1].created_at},
        )
        self.assertEqual(response.data['has_next_page'], False)
        results = response.data['results']
        self.assertEqual(len(results), page_size)
        self.assertEqual(results[0]['id'], newsfeeds[page_size].id)
        self.assertEqual(results[1]['id'], newsfeeds[page_size + 1].id)
        self.assertEqual(
            results[page_size - 1]['id'],
            newsfeeds[2 * page_size - 1].id,
        )

        # pull latest newsfeeds
        response = self.qwerty_client.get(
            NEWSFEEDS_URL,
            {'created_at__gt': newsfeeds[0].created_at},
        )
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 0)

        tweet = self.create_tweet(followed_user)
        new_newsfeed = self.create_newsfeed(user=self.qwerty, tweet=tweet)

        response = self.qwerty_client.get(
            NEWSFEEDS_URL,
            {'created_at__gt': newsfeeds[0].created_at},
        )
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], new_newsfeed.id)

    def test_user_cache(self):
        profile = self.asdfgh.profile
        profile.nickname = 'asdfgh_nick'
        profile.save()

        self.assertEqual(self.qwerty.username, 'qwerty')
        self.create_newsfeed(self.asdfgh, self.create_tweet(self.qwerty))
        self.create_newsfeed(self.asdfgh, self.create_tweet(self.asdfgh))

        response = self.asdfgh_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'asdfgh')
        self.assertEqual(results[0]['tweet']['user']['nickname'], 'asdfgh_nick')
        self.assertEqual(results[1]['tweet']['user']['username'], 'qwerty')

        self.qwerty.username = 'qwerty_username'
        self.qwerty.save()
        profile.nickname = 'asdfgh_nick2'
        profile.save()

        response = self.asdfgh_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'asdfgh')
        self.assertEqual(results[0]['tweet']['user']['nickname'], 'asdfgh_nick2')
        self.assertEqual(results[1]['tweet']['user']['username'], 'qwerty_username')

    def test_tweet_cache(self):
        tweet = self.create_tweet(self.qwerty, 'content1')
        self.create_newsfeed(self.asdfgh, tweet)
        response = self.asdfgh_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'qwerty')
        self.assertEqual(results[0]['tweet']['content'], 'content1')

        # update username
        self.qwerty.username = 'qwerty_username'
        self.qwerty.save()
        response = self.asdfgh_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'qwerty_username')

        # update content
        tweet.content = 'content2'
        tweet.save()
        response = self.asdfgh_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['content'], 'content2')

    def _paginate_to_get_newsfeeds(self, client):
        # paginate until the end
        response = client.get(NEWSFEEDS_URL)
        results = response.data['results']
        while response.data['has_next_page']:
            created_at__lt = response.data['results'][-1]['created_at']
            response = client.get(NEWSFEEDS_URL, {'created_at__lt': created_at__lt})
            results.extend(response.data['results'])
        return results

    def test_redis_list_limit(self):
        list_limit = settings.REDIS_LIST_LENGTH_LIMIT
        page_size = EndlessPagination.page_size
        users = [self.create_user('user{}'.format(i), str(i) + 'user@twitter.com') for i in range(5)]
        newsfeeds = []
        for i in range(list_limit + page_size):
            tweet = self.create_tweet(user=users[i % 5], content='feed{}'.format(i))
            feed = self.create_newsfeed(self.qwerty, tweet)
            newsfeeds.append(feed)
        newsfeeds = newsfeeds[::-1]

        # only cached list_limit objects
        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(self.qwerty.id)
        self.assertEqual(len(cached_newsfeeds), list_limit)
        queryset = NewsFeed.objects.filter(user=self.qwerty)
        self.assertEqual(queryset.count(), list_limit + page_size)

        results = self._paginate_to_get_newsfeeds(self.qwerty_client)
        self.assertEqual(len(results), list_limit + page_size)
        for i in range(list_limit + page_size):
            self.assertEqual(newsfeeds[i].id, results[i]['id'])

        # a followed user create a new tweet
        self.create_friendship(self.qwerty, self.asdfgh)
        new_tweet = self.create_tweet(self.asdfgh, 'a new tweet')
        NewsFeedService.fanout_to_followers(new_tweet)

        def _test_newsfeeds_after_new_feed_pushed():
            results = self._paginate_to_get_newsfeeds(self.qwerty_client)
            self.assertEqual(len(results), list_limit + page_size + 1)
            self.assertEqual(results[0]['tweet']['id'], new_tweet.id)
            for i in range(list_limit + page_size):
                self.assertEqual(newsfeeds[i].id, results[i + 1]['id'])

        _test_newsfeeds_after_new_feed_pushed()

        # cache expired
        self.clear_cache()
        _test_newsfeeds_after_new_feed_pushed()
