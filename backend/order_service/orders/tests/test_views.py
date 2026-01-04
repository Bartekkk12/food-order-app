import email

from rest_framework import status
from rest_framework.test import APITestCase

from django.urls import reverse
from django.contrib.auth import get_user_model

from ..models import Address, UserAddress, Restaurant

User = get_user_model()


class RegisterUserTestCase(APITestCase):
    def test_register_user_success(self):
        url = reverse('register')
        data = {
            'email': 'userTestCase@email.com',
            'name': 'User',
            'surname': 'Test',
            'phone_number': '753230530',
            'password': 'Password123!',
            'password_confirm': 'Password123!'
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='userTestCase@email.com').exists())


class LoginUserTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='userTestCase@email.com',
            name='User',
            surname='Test',
            phone_number='753230530',
            password='Password123!',
        )

    def test_login_success(self):
        url = reverse('login')

        data = {
            'email': 'userTestCase@email.com',
            'password': "Password123!",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


class UserAddressTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='userTestCase@email.com',
            name='User',
            surname='Test',
            phone_number='753230530',
            password='Password123!',
        )

    def authenticate(self):
        response = self.client.post(reverse('login'), {
            'email': 'userTestCase@email.com',
            'password': 'Password123!',
        })
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}'
        )

    def test_get_address_requires_auth(self):
        url = reverse('user-address-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_address(self):
        self.authenticate()

        url = reverse('user-address-list')
        data = {
            'city': 'Poznan',
            'zip_code': '12-345',
            'street': 'Kopernika',
            'house_number': '3A',
            'apartment_number': '4',
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UserAddressDetailTestCase(APITestCase):
    def setUp(self):
        self.password = 'Password123!'

        self.user = User.objects.create_user(
            email='userTestCase@email.com',
            name='User',
            surname='Test',
            phone_number='753230530',
            password=self.password,
        )

        self.other_user = User.objects.create_user(
            email='otherUserTestCase@email.com',
            name='Other',
            surname='User',
            phone_number='7532323530',
            password=self.password,
        )
        self.address = Address.objects.create(
            city='Poznan',
            zip_code='12-345',
            street='Kopernika',
            house_number='3A',
            apartment_number='4',
        )
        self.user_address = UserAddress.objects.create(
            user=self.user,
            address=self.address,
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_get_own_address(self):
        self.authenticate(self.user)

        url = reverse('user-address-detail', kwargs={
            'pk': self.user_address.id
        })

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['address']['city'], 'Poznan')

    def test_get_other_user_address(self):
        self.authenticate(self.other_user)

        url = reverse('user-address-detail', kwargs={'pk': self.user_address.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_address(self):
        self.authenticate(self.user)

        url = reverse('user-address-detail', kwargs={'pk': self.user_address.id})

        data = {
            'address': {
                'city': 'Warszawa',
            }
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.address.refresh_from_db()
        self.assertEqual(self.address.city, 'Warszawa')

    def test_delete_address(self):
        self.authenticate(self.user)

        url = reverse('user-address-detail', kwargs={'pk': self.user_address.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(UserAddress.objects.filter(id=self.user_address.id).exists())
        self.assertFalse(Address.objects.filter(id=self.address.id).exists())


class UserListTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email='adminTestCase@email.com',
            name='Admin',
            surname='Test',
            phone_number='753230530',
            password='Password123!',
        )
        self.user = User.objects.create_user(
            email='userTestCase@email.com',
            name='User',
            surname='Test',
            phone_number='7532323530',
            password='Password123!',
        )

        self.url = reverse('user-list')

    def test_admin_can_list_users(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), User.objects.count())

    def test_non_admin_can_not_list_users(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_list_users(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RestaurantListTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='userTestCase@email.com',
            name='User',
            surname='Test',
            phone_number='753230530',
            password='Password123!',
        )
        self.restaurant1 = Restaurant.objects.create(name='Restaurant1')
        self.restaurant2 = Restaurant.objects.create(name='Restaurant2')

        self.url = reverse('restaurant-list')

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    def test_get_restaurant_public(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_post_restaurant_authenticated(self):
        self.authenticate()

        data = {'name': 'Restaurant3'}

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Restaurant.objects.filter(name='Restaurant3').exists())

    def test_post_restaurant_not_authenticated(self):
        data = {'name': 'Restaurant4'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Restaurant.objects.filter(name='Restaurant4').exists())


class RestaurantDetailTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='userTestCase@email.com',
            name='User',
            surname='Test',
            phone_number='753230530',
            password='Password123!',
        )
        self.restaurant1 = Restaurant.objects.create(name='Restaurant1')

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    def test_get_restaurant_public(self):
        response = self.client.get(reverse('restaurant-detail', kwargs={'pk': self.restaurant1.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Restaurant1')

    def test_update_restaurant_authenticated(self):
        self.authenticate()

        url = reverse('restaurant-detail', kwargs={'pk': self.restaurant1.id})

        data = {
            'name': 'Restaurant5',
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Restaurant5')
        self.assertTrue(Restaurant.objects.filter(name='Restaurant5').exists())

    def test_update_restaurant_not_authenticated(self):
        url = reverse('restaurant-detail', kwargs={'pk': self.restaurant1.id})
        data = {'name': 'Restaurant6'}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Restaurant.objects.filter(name='Restaurant6').exists())

    def test_delete_restaurant_authenticated(self):
        self.authenticate()

        url = reverse('restaurant-detail', kwargs={'pk': self.restaurant1.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Restaurant.objects.filter(name='Restaurant1').exists())