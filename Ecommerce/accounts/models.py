from django.db import models
from django.contrib.auth.models import AbstractUser,Group, Permission
from .managers import CustomUserManager
from django.utils import timezone

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email



    class Meta:
        swappable = 'AUTH_USER_MODEL'

    groups = models.ManyToManyField(Group, verbose_name=('groups'), blank=True, related_name='customuser_set')
    user_permissions = models.ManyToManyField(Permission, verbose_name=('user permissions'), blank=True, related_name='customuser_set')
 

class ShippingAddress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='shipping_addresses')
    full_name = models.CharField(max_length=255)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    is_default = models.BooleanField(default=False)  

    def __str__(self):
        return f"{self.full_name} - {self.address_line1}, {self.city}, {self.country}"
    
    def save(self, *args, **kwargs):
        self.user.updated_at = timezone.now()
        self.user.save(update_fields=['updated_at'])

        super().save(*args, **kwargs)  

# from products.models import Product

# class Review(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
#     comment = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)