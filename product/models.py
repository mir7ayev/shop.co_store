from django.db import models
from core.models import BaseModel
from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model

User = get_user_model()

# TODO: get user from other micro-service

GENDER_CHOICES = (
    (1, "Men"),
    (2, "Women"),
    (3, "Baby"),
)


class ProductCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return f"The category id is {self.id}, name is {self.name}"


class ProductColor(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return f"The color id is {self.id}, name is {self}"


class ProductSize(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return f"The size id is {self.id}, name is {self.name}"


class Product(BaseModel):
    name = models.CharField(max_length=120)
    gender = models.IntegerField(choices=GENDER_CHOICES, default=1)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)

    image = models.ImageField(upload_to='products/')
    description = RichTextField()

    price = models.FloatField()
    discount = models.IntegerField(default=0)
    price_with_discount = models.FloatField(default=0, null=True, blank=True)

    colors = models.ManyToManyField(ProductColor, blank=True)
    sizes = models.ManyToManyField(ProductSize, blank=True)

    is_available = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.price_with_discount = self.price * (1 - self.discount / 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"The product id is {self.id}, name is {self.name}"


class ProductComment(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"The comment id is {self.id}, name is {self.name}"
