from django.contrib import admin
from django import forms
from .models import (
    ProductCategory, ProductColor, ProductSize, Product,
    ProductColorQuantity, ProductImage, ProductComment,
)


# Custom form to display percentage next to the discount field
class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set widget styles and help texts for price-related fields
        price_fields = ['price', 'price_with_discount', 'discount']
        for field in price_fields:
            self.fields[field].widget = forms.NumberInput(attrs={
                'style': 'width: 100px; display: inline-block;',
            })

        # Adding help texts for clarity
        self.fields['discount'].help_text = 'Discount percentage (%)'
        self.fields['price'].help_text = 'Price ($)'
        self.fields['price_with_discount'].help_text = 'Price after discount ($)'


# Inline admin for ProductImage to be used within ProductColorQuantity
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


# Inline admin for ProductColorQuantity to be used within Product
class ProductColorQuantityInline(admin.TabularInline):
    model = ProductColorQuantity
    extra = 1
    inlines = [ProductImageInline]


# Admin for ProductCategory with basic list display and filtering
@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')


# Admin for ProductColor with basic list display and filtering
@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')


# Admin for ProductSize with basic list display and filtering
@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')


# Admin for Product with nested ProductColorQuantityInline and custom form
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = (
        'id', 'name', 'category', 'formatted_discount',
        'formatted_price_with_discount', 'is_available'
    )
    list_display_links = ('id', 'name')
    list_filter = ('id', 'price_with_discount', 'category', 'is_available')
    search_fields = ('name', 'description')
    inlines = (ProductColorQuantityInline,)

    def formatted_price_with_discount(self, obj):
        return f"${obj.price_with_discount:.2f}"

    formatted_price_with_discount.short_description = "Price with discount"

    def formatted_discount(self, obj):
        return f"{obj.discount}%"

    formatted_discount.short_description = "Discount"


# Admin for ProductColorQuantity with nested ProductImageInline
@admin.register(ProductColorQuantity)
class ProductColorQuantityAdmin(admin.ModelAdmin):
    list_display = ('product', 'color', 'quantity')
    list_display_links = ('product',)
    list_filter = ('id', 'product', 'color', 'quantity')
    search_fields = ('product__name', 'color__name')
    inlines = (ProductImageInline,)


# Admin for ProductImage with advanced list display and filtering
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_color_quantity', 'image')
    list_display_links = ('id', 'product_color_quantity')
    list_filter = ('id', 'product_color_quantity__product', 'product_color_quantity__color')
    search_fields = ('product_color_quantity__product__name', 'product_color_quantity__color__name')


# Admin for ProductComment with advanced list display and filtering
@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'product', 'created_at', 'is_active')
    list_display_links = ('id', 'author')
    list_filter = ('id', 'author', 'product', 'is_active')
    search_fields = ('author__username', 'product__name', 'comment')
