from rest_framework import status
from rest_framework.test import APITestCase

from django.urls import reverse
from django.contrib.auth import get_user_model

from ..models import Address, UserAddress, Restaurant, RestaurantAddress

User = get_user_model()


# ------------------ BASE CONFIG ------------------
class BaseConfig(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            name='User',
            surname='Test',
            phone_number='111111111',
            password='Password123!',
        )

        self.other_user = User.objects.create_user(
            email='other@test.com',
            name='Other',
            surname='User',
            phone_number='222222222',
            password='Password123!',
        )

        self.admin = User.objects.create_superuser(
            email='admin@test.com',
            name='Admin',
            surname='Test',
            phone_number='333333333',
            password='Password123!',
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

        self.restaurant1 = Restaurant.objects.create(name='Restaurant1')
        self.restaurant2 = Restaurant.objects.create(name='Restaurant2')

    def authenticate(self, user=None):
        self.client.force_authenticate(user=user or self.user)


# ------------------ AUTH ------------------
class RegisterUserTestCase(APITestCase):
    def test_register_user_success(self):
        url = reverse('register')
        data = {
            'email': 'newuser@test.com',
            'name': 'User',
            'surname': 'Test',
            'phone_number': '999999999',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@test.com').exists())


class LoginUserTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='login@test.com',
            name='User',
            surname='Test',
            phone_number='555555555',
            password='Password123!',
        )

    def test_login_success(self):
        url = reverse('login')
        data = {
            'email': 'login@test.com',
            'password': 'Password123!',
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


# ------------------ USER ADDRESS ------------------
class UserAddressTestCase(BaseConfig):
    def test_auth_required(self):
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


class UserAddressDetailTestCase(BaseConfig):
    def test_get_own_address(self):
        self.authenticate()

        url = reverse('user-address-detail', kwargs={'pk': self.user_address.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['address']['city'], 'Poznan')

    def test_get_other_user_address(self):
        self.authenticate(self.other_user)

        url = reverse('user-address-detail', kwargs={'pk': self.user_address.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_address(self):
        self.authenticate()

        url = reverse('user-address-detail', kwargs={'pk': self.user_address.id})
        data = {'address': {'city': 'Warszawa'}}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.address.refresh_from_db()
        self.assertEqual(self.address.city, 'Warszawa')

    def test_delete_address(self):
        self.authenticate()

        url = reverse('user-address-detail', kwargs={'pk': self.user_address.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UserAddress.objects.exists())
        self.assertFalse(Address.objects.exists())


# ------------------ USER LIST ------------------
class UserListTestCase(BaseConfig):
    def setUp(self):
        super().setUp()
        self.url = reverse('user-list')

    def test_admin_can_list_users(self):
        self.authenticate(self.admin)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), User.objects.count())

    def test_user_cannot_list_users(self):
        self.authenticate()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ------------------ RESTAURANT ------------------
class RestaurantListTestCase(BaseConfig):
    def setUp(self):
        super().setUp()
        self.url = reverse('restaurant-list')

    def test_get_public(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_authenticated(self):
        self.authenticate()
        response = self.client.post(self.url, {'name': 'Restaurant3'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_unauthenticated(self):
        response = self.client.post(self.url, {'name': 'Restaurant4'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RestaurantDetailTestCase(BaseConfig):
    def test_get_public(self):
        url = reverse('restaurant-detail', kwargs={'pk': self.restaurant1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_authenticated(self):
        self.authenticate()

        url = reverse('restaurant-detail', kwargs={'pk': self.restaurant1.id})
        response = self.client.patch(url, {'name': 'Updated'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_unauthenticated(self):
        url = reverse('restaurant-detail', kwargs={'pk': self.restaurant1.id})
        response = self.client.patch(url, {'name': 'Fail'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_authenticated(self):
        self.authenticate()

        url = reverse('restaurant-detail', kwargs={'pk': self.restaurant1.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


# ------------------ RESTAURANT ADDRESS ------------------
class RestaurantAddressListTestCase(BaseConfig):
    def setUp(self):
        super().setUp()

        self.address2 = Address.objects.create(
            city="Warszawa",
            zip_code="00-001",
            street="Marszalkowska",
            house_number="10"
        )

        RestaurantAddress.objects.create(
            restaurant=self.restaurant1,
            address=self.address
        )

        RestaurantAddress.objects.create(
            restaurant=self.restaurant2,
            address=self.address2
        )

        self.url = reverse("restaurant-address-list", kwargs={"pk": self.restaurant1.id})

    def test_auth_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_addresses_for_restaurant(self):
        self.authenticate()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['address']['city'], 'Poznan')

    def test_create_address(self):
        self.authenticate()

        data = {
            "city": "Gdansk",
            "zip_code": "80-001",
            "street": "Dluga",
            "house_number": "1"
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Address.objects.filter(city='Gdansk').exists())
