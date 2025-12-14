from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import CustomUserManager

# Create your models here.


class User(AbstractBaseUser, PermissionsMixin):
    username = None
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname', 'phone_number']

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Address(models.Model):
    country = models.CharField(max_length=50, default="Poland")
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    street = models.CharField(max_length=100)
    house_number = models.CharField(max_length=50)
    apartment_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.street}, {self.house_number}, {self.apartment_number}"


class Restaurant(models.Model):
    restaurant_name = models.CharField(max_length=100)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)


class Order(models.Model):
    name = models.CharField(max_length=100)
