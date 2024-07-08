from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from stagetwo.models import Organisation
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.url = reverse('register')  # Ensure this matches the URL pattern name for your registration view
        self.valid_data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "password123",
            "phone": "+1234567890"
        }
        self.invalid_email_data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "invalid-email",
            "password": "password123",
            "phone": "+1234567890"
        }
        self.invalid_phone_data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "password123",
            "phone": "invalid-phone"
        }

    def test_registration_with_valid_data(self):
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('accessToken', response.data['data'])

    def test_registration_with_invalid_email(self):
        response = self.client.post(self.url, self.invalid_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'][0]['field'], 'email')
        self.assertEqual(response.data['errors'][0]['message'], 'Enter a valid email address.')

    def test_registration_with_invalid_phone(self):
        response = self.client.post(self.url, self.invalid_phone_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'][0]['field'], 'phone')
        self.assertEqual(response.data['errors'][0]['message'], "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")


class AuthTests(APITestCase): # original tests specified in the assignment statement

    def test_register_user_successfully(self):
        url = reverse('register')
        data = {
            "firstName": "John", 
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "password123",
            "phone": "1234567890"
        }
        response = self.client.post(url, data, format='json')
        #check for correct user details, access tokens and status code in response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('accessToken', response.data['data'])
        self.assertEqual(response.data['data']['user']['firstName'], 'John')
        self.assertEqual(response.data['data']['user']['lastName'], 'Doe')
        self.assertEqual(response.data['data']['user']['email'], 'john.doe@example.com')

        # check default organisation creation
        userId = response.data['data']['user']['userId']
        user = User.objects.get(userId=userId)
        organisation = Organisation.objects.get(users=user)
        self.assertEqual(organisation.name, "John's Organisation")

    def test_login_user_successfully(self):
        User.objects.create_user(
            first_name="John", last_name="Doe", email="john.doe@example.com", password="password123"
        )
        url = reverse('login')
        data = {
            "email": "john.doe@example.com",
            "password": "password123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('accessToken', response.data['data'])
        self.assertEqual(response.data['data']['user']['email'], 'john.doe@example.com')

    def test_register_missing_fields(self):
        url = reverse('register')

        # Missing firstName
        data = {
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "password123",
            "phone": "1234567890"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Missing lastName
        data = {
            "firstName": "John",
            "email": "john.doe@example.com",
            "password": "password123",
            "phone": "1234567890"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Missing email
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "password": "password123",
            "phone": "1234567890"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Missing password
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "phone": "1234567890"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        url = reverse('register')
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "password123",
            "phone": "1234567890"
        }
        self.client.post(url, data, format='json')

        # Attempt to register with the same email
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class APItests(APITestCase):
    client = APIClient()
    def test_token_generation_and_expiry(self):
        user = User.objects.create_user(
            first_name="John", last_name="Doe", email="john.doe@example.com", password="password123"
        )
        token = AccessToken.for_user(user)
        self.assertIn('exp', token.payload)
        self.assertEqual(token.payload['user_id'], user.id)

    def test_organisation_access_control(self):
        
        user1 = User.objects.create_user(
            first_name="John", last_name="Doe", email="john.doe@example.com", password="password123"
        )
        user2 = User.objects.create_user(
            first_name="Ife", last_name="Dayo", email="ife.dayo@example.com", password="password234"
        )
        organisation = Organisation.objects.create(name="John's Organisation")
        organisation.users.add(user1)

        
        url = reverse('organisation-detail', args=[organisation.orgId])
        self.client.force_authenticate(user=user1)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=user2)
        ans = self.client.get(url)
        self.assertEqual(ans.status_code, status.HTTP_404_NOT_FOUND)


class UserDetailViewTests(APITestCase):
    client = APIClient()
    def setUp(self):
        self.user1 = User.objects.create_user(
            email="user1@example.com", first_name="User", last_name="One", password="password123"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", first_name="User", last_name="Two", password="password123"
        )
        self.org = Organisation.objects.create(name="Test Organisation")
        self.org.users.add(self.user1, self.user2)
        self.client.force_authenticate(user=self.user1)

    def test_get_own_user_record(self):
        url = reverse('user-detail', args=[str(self.user1.userId)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['email'], self.user1.email)

    def test_get_other_user_in_same_organisation(self):
        url = reverse('user-detail', args=[str(self.user2.userId)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['email'], self.user2.email)
    
    def test_get_other_user_not_in_same_organisation(self):
        user3 = User.objects.create_user(
            email="user3@example.com", first_name="User", last_name="Three", password="password123"
        )
        url = reverse('user-detail', args=[str(user3.userId)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

