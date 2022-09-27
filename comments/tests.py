from django.test import TestCase
# Create your tests here.
from testing.testcases import TestCase


class CommentModelTests(TestCase):

    def setUp(self):
        self.jenny = self.create_user('jenny', 'jenny@twitter.com')
        self.tweet = self.create_tweet(self.jenny)
        self.comment = self.create_comment(self.jenny, self.tweet)

    def test_comment(self):
        self.assertNotEqual(self.comment.__str__(), None)

    def test_like_set(self):
        self.create_like(self.jenny, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        self.create_like(self.jenny, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        aya = self.create_user('aya', 'aya@twitter.com')
        self.create_like(aya, self.comment)
        self.assertEqual(self.comment.like_set.count(), 2)
