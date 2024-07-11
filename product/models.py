from django.db import models
from core.models import BaseModel
from ckeditor.fields import RichTextField

# TODO: add quantity to product works with color


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
        return f"The color id is {self.id}, name is {self.name}"


class ProductSize(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return f"The size id is {self.id}, name is {self.name}"


class Product(BaseModel):
    name = models.CharField(max_length=120)
    gender = models.IntegerField(choices=GENDER_CHOICES, default=1)
    category = models.ForeignKey(ProductCategory, default=1, on_delete=models.CASCADE)
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


class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"The product id is {self.id}, name is {self.product}"


class ProductReview(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    author = models.IntegerField()
    rating = models.IntegerField()
    comment = models.TextField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Review by {self.author} on {self.product.name}"
