from django.contrib import admin
from .models import (
    ProductCategory, ProductColor, ProductSize, Product,
    ProductComment,
)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')


@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')


@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'gender', 'created_at', 'is_available')
    list_display_links = ('id', 'name')


@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'product', 'created_at', 'is_active')
    list_display_links = ('id', 'author')
