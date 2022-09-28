from notifications.models import Notification
from testing.testcases import TestCase


COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'


class NotificationTests(TestCase):

    def setUp(self):
        self.qwerty, self.qwerty_client = self.create_user_and_client('qwerty', 'qwerty@twitter.com')
        self.asdfgh, self.asdfgh_client = self.create_user_and_client('asdfgh', 'asdfgh@twitter.com')
        self.asdfgh_tweet = self.create_tweet(self.asdfgh)

    def test_comment_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.qwerty_client.post(COMMENT_URL, {
            'tweet_id': self.asdfgh_tweet.id,
            'content': 'a ha',
        })
        self.assertEqual(Notification.objects.count(), 1)

    def test_like_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.qwerty_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.asdfgh_tweet.id,
        })
        self.assertEqual(Notification.objects.count(), 1)
