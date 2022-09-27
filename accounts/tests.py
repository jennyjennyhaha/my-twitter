"""
from accounts.models import UserProfile
from testing.testcases import TestCase


class UserProfileTests(TestCase):

    def test_profile_property(self):
        jenny = self.create_user('jenny')
        self.assertEqual(UserProfile.objects.count(), 0)
        p = jenny.profile
        self.assertEqual(isinstance(p, UserProfile), True)
        self.assertEqual(UserProfile.objects.count(), 1)
"""