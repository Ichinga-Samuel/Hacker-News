from django.test import Client
from django.test import TestCase
from django.contrib.auth import get_user_model


class HomeViewTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        user = self.User.objects.create_user(username='Samiyol', email='samuelichinga@gmail.com', password='Samuel123#')
        self.client = Client()

    def test_login(self):
        res = self.client.post('/account/login/', {'email': 'samuelichinga@gmail.com',
                                                   'password': 'Samuel123#'})
        self.assertEqual(res.status_code, 200)
