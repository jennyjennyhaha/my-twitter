from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User


LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'

"""
class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
"""


class AccountApiTests(TestCase):

    def setUp(self):
        # run when every test function is executed
        self.client = APIClient()
        self.user = self.createUser(
            username='admin',
            email='admin@twitter.com',
            password='correct password',
        )

    def createUser(self, username, email, password):
        # cannot use User.objects.create()
        # since password needs encryption, and username and email need normalize process
        return User.objects.create_user(username, email, password)

    def test_login(self):
        # test function must start with test_ to be called automatically
        # test must use post but not get
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # login failure, http status code return 405 = METHOD_NOT_ALLOWED
        self.assertEqual(response.status_code, 405)

        # use post but the password is wrong
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, 400)

        # auth not login yet
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)
        # use correct password
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['email'], 'admin@twitter.com')

        # auth already login
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):
        # login first
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # auth user has logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # test must use post
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # use post logout success
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)

        # auth user has logged out
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

