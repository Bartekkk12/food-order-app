from django.test import TestCase

from ..models import *

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
        # Test for the correct updating user
        old_updated_at = self.user.updated_at
        self.user.name = 'Mike'
        self.user.save()
        self.assertNotEqual(self.user.updated_at, old_updated_at)
        self.assertEqual(self.user.name, 'Mike')


class RestaurantTestCase(TestCase):
    """Test case for Restaurant model."""
    def setUp(self):
        # Create address
        self.address = Address.objects.create(
            country='US',
            city='New York',
            zip_code='12345',
            street='Smith st.',
            house_number='12',
            apartment_number='1',
        )

    def test_restaurant_creation(self):
        # Test for correct restaurant creation
        self.restaurant = Restaurant.objects.create(
            name='Restaurant Name',
            address=self.address,
        )
        self.assertEqual(self.restaurant.name, 'Restaurant Name')
        self.assertEqual(self.restaurant.address, self.address)
        self.assertIsNotNone(self.restaurant.slug)

    def test_slug_creation(self):
        # Test for correct slug creation
        restaurant1 = Restaurant.objects.create(name='Restaurant Name')
        self.assertEqual(restaurant1.slug, 'restaurant-name')

        restaurant2 = Restaurant.objects.create(name='Restaurant Name')
        self.assertEqual(restaurant2.slug, 'restaurant-name-1')

    def test_null_address(self):
        # Test for the optional address field
        restaurant = Restaurant.objects.create(name='Restaurant')
        self.assertIsNone(restaurant.address)

    def test_created_and_updated_at(self):
        # Test created and updated at fields
        restaurant = Restaurant.objects.create(
            name='Restaurant with Time',
            address=self.address,
        )
        self.assertIsNotNone(restaurant.created_at)
        self.assertIsNotNone(restaurant.updated_at)

    def test_update_restaurant(self):
        # Test for the correct updating restaurant
        restaurant = Restaurant.objects.create(name='Restaurant')
        old_updated_at = restaurant.updated_at
        restaurant.name = 'New Name'
        restaurant.save()
        self.assertNotEqual(restaurant.updated_at, old_updated_at)
        self.assertEqual(restaurant.name, 'New Name')


class ProductTestCase(TestCase):
    def setUp(self):
        # Create address
        self.address = Address.objects.create(
            country='US',
            city='New York',
            zip_code='12345',
            street='Smith st.',
            house_number='12',
            apartment_number='1',
        )
        self.restaurant = Restaurant.objects.create(
            name='Restaurant Name',
            address=self.address,
        )

    def test_product_creation(self):
        # Test for correct product creation
        product = Product.objects.create(
            name='Product Name',
            price=20.99,
            restaurant=self.restaurant,
        )
        self.assertEqual(product.name, 'Product Name')
        self.assertEqual(product.price, 20.99)
        self.assertEqual(product.restaurant, self.restaurant)
        self.assertIsNotNone(product.slug)

    def test_slug_creation(self):
        # Test for correct slug creation
        product1 = Product.objects.create(
            name='Product Name',
            price=20.99,
            restaurant=self.restaurant,
        )
        self.assertEqual(product1.slug, 'product-name')

        product2 = Product.objects.create(
            name='Product Name',
            price=20.99,
            restaurant=self.restaurant,
        )
        self.assertEqual(product2.slug, 'product-name-1')

    def test_created_and_updated_at(self):
        # Test created and updated at fields
        product = Product.objects.create(
            name='Product Name',
            price=20.99,
            restaurant=self.restaurant,
        )
        self.assertIsNotNone(product.created_at)
        self.assertIsNotNone(product.updated_at)

    def test_update_product(self):
        # Test for the correct updating product
        product = Product.objects.create(
            name='Product Name',
            price=20.99,
            restaurant=self.restaurant,
        )
        old_updated_at = product.updated_at
        product.name = 'New Name'
        product.save()
        self.assertNotEqual(product.updated_at, old_updated_at)


class OrderTestCase(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create(
            name='Jake',
            surname='Smith',
            email='smith@email.com',
            password='password1',
            phone_number='1234567890',
        )

    def test_order_creation(self):
        # Test for the correct order creation
        order = Order.objects.create(user=self.user)
        self.assertEqual(order.user, self.user)

    def test_created_at_field(self):
        # Test created at field
        order = Order.objects.create(user=self.user)
        self.assertIsNotNone(order.created_at)


class OrderProductsTestCase(TestCase):
    # Create objects
    def setUp(self):
        self.user = User.objects.create(
            name='Jake',
            surname='Smith',
            email='smith@email.com',
            password='password1',
            phone_number='1234567890',
        )
        self.order = Order.objects.create(user=self.user)
        self.address = Address.objects.create(
            country='US',
            city='New York',
            zip_code='12345',
            street='Smith st.',
            house_number='12',
            apartment_number='1',
        )
        self.restaurant = Restaurant.objects.create(
            name='Restaurant Name',
            address=self.address,
        )
        self.product = Product.objects.create(
            name='Product Name',
            price=20.99,
            restaurant=self.restaurant,
        )

    def test_order_products_creation(self):
        # Test for the correct order products creation
        order_products = OrderProducts.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
        )
        self.assertEqual(order_products.order, self.order)
        self.assertEqual(order_products.product, self.product)
        self.assertEqual(order_products.quantity, 2)
    
    def test_default_quantity(self):
        # Test for the default quantity value
        order_products = OrderProducts.objects.create(
            order=self.order,
            product=self.product,
        )
        self.assertEqual(order_products.quantity, 1)

    def test_created_and_updated_at(self):
        # Test for the created and updated at fields
        order_products = OrderProducts.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
        )
        self.assertIsNotNone(order_products.created_at)
        self.assertIsNotNone(order_products.updated_at)

    def test_update_order_products(self):
        # Test for the correct updating order products
        order_products = OrderProducts.objects.create(
            order=self.order,
            product=self.product,
        )
        old_updated_at = order_products.updated_at
        order_products.quantity = 5
        order_products.save()
        self.assertNotEqual(order_products.updated_at, old_updated_at)
        self.assertEqual(order_products.quantity, 5)

    def test_get_total_price(self):
        # Test get_total_price method
        order_products = OrderProducts.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
        )
        expected_total_price = 2 * 20.99
        self.assertEqual(order_products.get_total_price(), expected_total_price)
