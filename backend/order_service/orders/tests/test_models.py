from django.test import TestCase

from orders.models import *

# Models tests


class AddressTestCase(TestCase):
    def setUp(self):
        self.address = Address.objects.create(
            country='US',
            city='New York',
            zip_code='12345',
            street='Smith st.',
            house_number='12',
            apartment_number='1',
        )

    def test_address_creation(self):
        self.assertEqual(self.address.country, 'US')
        self.assertEqual(self.address.city, 'New York')
        self.assertEqual(self.address.zip_code, '12345')
        self.assertEqual(self.address.street, 'Smith st.')
        self.assertEqual(self.address.house_number, '12')
        self.assertEqual(self.address.apartment_number, '1')
