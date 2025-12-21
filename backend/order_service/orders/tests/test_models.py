from django.test import TestCase

from orders.models import *

# Models tests


class AddressTestCase(TestCase):
    """Test case for Address model."""
    def setUp(self):
        # Creates a sample address
        self.address = Address.objects.create(
            country='US',
            city='New York',
            zip_code='12345',
            street='Smith st.',
            house_number='12',
            apartment_number='1',
        )

    def test_address_creation(self):
        # Test for correct address creation
        self.assertEqual(self.address.country, 'US')
        self.assertEqual(self.address.city, 'New York')
        self.assertEqual(self.address.zip_code, '12345')
        self.assertEqual(self.address.street, 'Smith st.')
        self.assertEqual(self.address.house_number, '12')
        self.assertEqual(self.address.apartment_number, '1')

    def test_default_country(self):
        # Test the default value of the country field
        address = Address.objects.create(
            city='Krakow',
            zip_code='12-345',
            street='Pachonskiego',
            house_number='3',
        )
        self.assertEqual(address.country, 'Poland')

    def test_null_apartment_number(self):
        # Test for the optional apartment_number field
        address = Address.objects.create(
            city='Krakow',
            zip_code='12-345',
            street='Pachonskiego',
            house_number=3,
        )
        self.assertIsNone(address.apartment_number)

    def test_str_method(self):
        # Test __st__ method
        expected_str = 'Smith st., 12, 1'
        self.assertEqual(str(self.address), expected_str)

    def test_created_and_updated_at(self):
        # Test created and updated at fields
        self.assertIsNotNone(self.address.created_at)
        self.assertIsNotNone(self.address.updated_at)

    def test_update_address(self):
        # Test for updating the updated_at field
        old_updated_at = self.address.updated_at
        self.address.street = 'New Street'
        self.address.save()
        self.assertNotEqual(self.address.updated_at, old_updated_at)
        self.assertEqual(self.address.street, 'New Street')


class UserTestCase(TestCase):
    """Test case for User model."""
    def setUp(self):
        # Creates a user
        self.user = User.objects.create(
            name='Jake',
            surname='Smith',
            email='smith@email.com',
            password='password1',
            phone_number='1234567890',
        )

    def test_user_creation(self):
        # Test for correct user creation
        self.assertEqual(self.user.name, 'Jake')
        self.assertEqual(self.user.surname, 'Smith')
        self.assertEqual(self.user.email, 'smith@email.com')
        self.assertEqual(self.user.password, 'password1')
        self.assertEqual(self.user.phone_number, '1234567890')

    def test_str_method(self):
        # Test __str__ method
        expected_str = 'smith@email.com'
        self.assertEqual(str(self.user.email), expected_str)

    def test_default_value_is_staff_and_is_active_fields(self):
        # Test default values of is_staff and is_active fields
        self.assertEqual(self.user.is_staff, False)
        self.assertEqual(self.user.is_active, True)

    def test_created_and_updated_at(self):
        # Test created and updated at fields
        self.assertIsNotNone(self.user.created_at)
        self.assertIsNotNone(self.user.updated_at)

    def test_update_user(self):
        # Test for updating the updated_at field
        old_updated_at = self.user.updated_at
        self.user.name = 'Mike'
        self.user.save()
        self.assertNotEqual(self.user.updated_at, old_updated_at)
        self.assertEqual(self.user.name, 'Mike')
