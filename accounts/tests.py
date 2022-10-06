from accounts.models import UserProfile
from testing.testcases import TestCase


class UserProfileTests(TestCase):

    def setUp(self):
        self.clear_cache()

    def test_profile_property(self):
        qwerty = self.create_user('qwerty', 'qwerty@twitter.com')
        self.assertEqual(UserProfile.objects.count(), 0)
        p = qwerty.profile
        self.assertEqual(isinstance(p, UserProfile), True)
        self.assertEqual(UserProfile.objects.count(), 1)
