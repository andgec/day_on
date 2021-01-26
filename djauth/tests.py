'''
Test module for djauth
'''
from django.test import TestCase
from djauth.models import User
from general.models import Company
import urllib3

from conf.settings import TEST_URL


class UserTestCase(TestCase):
    '''
    Testing user model
    '''
    
    def setUp(self):
        Company.objects.create(
            name = 'tc',
            email = 'tc'
        )
    
    def test_create_user(self):

        testcompany = None #Company.objects.get(name="tc")

        user = User.objects.create(
            is_superuser = False,
            username = 'testuser',
            email = 'testuser@test.on',
            first_name = 'Test',
            last_name = 'Testensen',
            is_staff = False,
            company = testcompany,
        )
        user.set_password('testuserpassword')
        user.save()

        print('UserID = {}'.format(user.id))

        self.assertTrue(self.client.login(id = user.id, password = 'testuserpassword'))

class TestApiToken(TestCase):
    def setUp(self):
        Company.objects.create(
            name = 'tc',
            email = 'tc'
        )
        
        user = User.objects.create(
            is_superuser = False,
            username = 'testuser',
            email = 'testuser@test.on',
            first_name = 'Test',
            last_name = 'Testensen',
            is_staff = False,
            company = testcompany,
        )
        user.set_password('testuserpassword')
        user.save()

    def test_token_url(self):
        http = urllib3.PoolManager()
        r = http.request('POST', TEST_URL + 'api/auth/token')
        print(r.data)
