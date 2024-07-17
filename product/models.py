from django.db import models
from core.models import BaseModel
from ckeditor.fields import RichTextField
from django.core.validators import MinValueValidator, MaxValueValidator

GENDER_CHOICES = (
    (1, "Men"),
    (2, "Women"),
    (3, "Baby"),
)


class ProductCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return f"{self.name} (ID: {self.id})"


class ProductColor(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return f"{self.name} (ID: {self.id})"


class ProductSize(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return f"{self.name} (ID: {self.id})"


class Product(BaseModel):
    name = models.CharField(max_length=120)
    gender = models.IntegerField(choices=GENDER_CHOICES, default=1)
    category = models.ForeignKey(ProductCategory, default=1, on_delete=models.CASCADE)
    description = RichTextField()

    price = models.FloatField(validators=[MinValueValidator(0)])
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    price_with_discount = models.FloatField(default=0, null=True, blank=True)

    colors = models.ManyToManyField(ProductColor, through='ProductColorQuantity', blank=True)
    sizes = models.ManyToManyField(ProductSize, blank=True)
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])

    is_available = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.price_with_discount = self.price * (1 - self.discount / 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (ID: {self.id})"


class ProductColorQuantity(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(ProductColor, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'color')

    def __str__(self):
        return f"{self.product.name} - {self.color.name} (Quantity: {self.quantity})"


class ProductImage(models.Model):
    product_color_quantity = models.ForeignKey(ProductColorQuantity, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image of {self.product_color_quantity.product.name} ({self.product_color_quantity.color.name})"


class ProductRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.IntegerField()
    rating = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.rating}"


class ProductComment(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    author = models.IntegerField()
    comment = models.TextField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Comment for {self.product.name} by User {self.author}"
