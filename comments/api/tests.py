from testing.testcases import TestCase
from rest_framework.test import APIClient
from comments.models import Comment
from django.utils import timezone


COMMENT_URL = '/api/comments/'
TWEET_LIST_API = '/api/tweets/'
TWEET_DETAIL_API = '/api/tweets/{}/'
NEWSFEED_LIST_API = '/api/newsfeeds/'


class CommentApiTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.anonymous_client = APIClient()
        self.qwerty = self.create_user('qwerty', 'qwerty@twitter.com')
        self.qwerty_client = APIClient()
        self.qwerty_client.force_authenticate(self.qwerty)
        self.asdfgh = self.create_user('asdfgh', 'asdfgh@twitter.com')
        self.asdfgh_client = APIClient()
        self.asdfgh_client.force_authenticate(self.asdfgh)

        self.tweet = self.create_tweet(self.qwerty)

    def test_create(self):
        # anonymous user cannot create
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        # no parameters
        response = self.qwerty_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # only tweet_id
        response = self.qwerty_client.post(COMMENT_URL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 400)

        # only content
        response = self.qwerty_client.post(COMMENT_URL, {'content': '1'})
        self.assertEqual(response.status_code, 400)

        # content too long
        response = self.qwerty_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1' * 141,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)

        # tweet_id and content
        response = self.qwerty_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.qwerty.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], '1')

    def test_destroy(self):
        comment = self.create_comment(self.qwerty, self.tweet)
        url = '{}{}/'.format(COMMENT_URL, comment.id)

        # anonymous user cannot delete
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # not the user himself
        response = self.asdfgh_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # the user himself
        count = Comment.objects.count()
        response = self.qwerty_client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), count - 1)

    def test_update(self):
        comment = self.create_comment(self.qwerty, self.tweet, 'original')
        another_tweet = self.create_tweet(self.asdfgh)
        url = '{}{}/'.format(COMMENT_URL, comment.id)

        # use put
        # anonymous user cannot update
        response = self.anonymous_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)
        # not himself
        response = self.asdfgh_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, 'new')
        # cannot update things other than content
        before_updated_at = comment.updated_at
        before_created_at = comment.created_at
        now = timezone.now()
        response = self.qwerty_client.put(url, {
            'content': 'new',
            'user_id': self.asdfgh.id,
            'tweet_id': another_tweet.id,
            'created_at': now,
        })
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'new')
        self.assertEqual(comment.user, self.qwerty)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertEqual(comment.created_at, before_created_at)
        self.assertNotEqual(comment.created_at, now)
        self.assertNotEqual(comment.updated_at, before_updated_at)

    def test_list(self):
        # must have tweet_id
        response = self.anonymous_client.get(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # with tweet_id, succeed
        # no comments
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)

        # comments ordered in time
        self.create_comment(self.qwerty, self.tweet, '1')
        self.create_comment(self.asdfgh, self.tweet, '2')
        self.create_comment(self.asdfgh, self.create_tweet(self.asdfgh), '3')
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
        })
        self.assertEqual(len(response.data['comments']), 2)
        self.assertEqual(response.data['comments'][0]['content'], '1')
        self.assertEqual(response.data['comments'][1]['content'], '2')

        #  user_id and tweet_id provided, only tweet_id will be effective in filter
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'user_id': self.qwerty.id,
        })
        self.assertEqual(len(response.data['comments']), 2)

    def test_comments_count(self):
        # test tweet detail api
        tweet = self.create_tweet(self.qwerty)
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.asdfgh_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments_count'], 0)

        # test tweet list api
        self.create_comment(self.qwerty, tweet)
        response = self.asdfgh_client.get(TWEET_LIST_API, {'user_id': self.qwerty.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['comments_count'], 1)

        # test newsfeeds list api
        self.create_comment(self.asdfgh, tweet)
        self.create_newsfeed(self.asdfgh, tweet)
        response = self.asdfgh_client.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['tweet']['comments_count'], 2)

    def test_comments_count_with_cache(self):
        tweet_url = '/api/tweets/{}/'.format(self.tweet.id)
        response = self.qwerty_client.get(tweet_url)
        self.assertEqual(self.tweet.comments_count, 0)
        self.assertEqual(response.data['comments_count'], 0)

        data = {'tweet_id': self.tweet.id, 'content': 'a comment'}
        for i in range(2):
            _, client = self.create_user_and_client('user{}'.format(i), str(i) + 'user@twitter.com')
            client.post(COMMENT_URL, data)
            response = client.get(tweet_url)
            self.assertEqual(response.data['comments_count'], i + 1)
            self.tweet.refresh_from_db()
            self.assertEqual(self.tweet.comments_count, i + 1)

        comment_data = self.asdfgh_client.post(COMMENT_URL, data).data
        response = self.asdfgh_client.get(tweet_url)
        self.assertEqual(response.data['comments_count'], 3)
        self.tweet.refresh_from_db()
        self.assertEqual(self.tweet.comments_count, 3)

        # update comment should not update comments_count
        comment_url = '{}{}/'.format(COMMENT_URL, comment_data['id'])
        response = self.asdfgh_client.put(comment_url, {'content': 'updated'})
        self.assertEqual(response.status_code, 200)
        response = self.asdfgh_client.get(tweet_url)
        self.assertEqual(response.data['comments_count'], 3)
        self.tweet.refresh_from_db()
        self.assertEqual(self.tweet.comments_count, 3)

        # delete a comment will update comments_count
        response = self.asdfgh_client.delete(comment_url)
        self.assertEqual(response.status_code, 200)
        response = self.qwerty_client.get(tweet_url)
        self.assertEqual(response.data['comments_count'], 2)
        self.tweet.refresh_from_db()
        self.assertEqual(self.tweet.comments_count, 2)



