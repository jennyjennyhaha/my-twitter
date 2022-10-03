from datetime import timedelta
from testing.testcases import TestCase
from tweets.constants import TweetPhotoStatus
from tweets.models import TweetPhoto
from utils.time_helpers import utc_now


# Create your tests here.
class TweetTests(TestCase):
    def setUp(self):
        self.jenny = self.create_user('jenny', 'jenny@twitter.com')
        self.tweet = self.create_tweet(self.jenny, content='hahahahahha')

    def test_hours_to_now(self):
        """
        jenny = User.objects.create_user(username='jenny')
        tweet = Tweet.objects.create(user=jenny, content='hahahaha!')
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 10)
        """
        self.tweet.created_at = utc_now() - timedelta(hours=10)
        self.tweet.save()
        self.assertEqual(self.tweet.hours_to_now, 10)

    def test_like_set(self):
        self.create_like(self.jenny, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.jenny, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        aya = self.create_user('aya', 'aya@twitter.com')
        self.create_like(aya, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)

    def test_create_photo(self):
        # 测试可以成功创建 photo 的数据对象
        photo = TweetPhoto.objects.create(
            tweet=self.tweet,
            user=self.jenny,
        )
        self.assertEqual(photo.user, self.jenny)
        self.assertEqual(photo.status, TweetPhotoStatus.PENDING)
        self.assertEqual(self.tweet.tweetphoto_set.count(), 1)

