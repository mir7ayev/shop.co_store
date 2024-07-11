from rest_framework.serializers import ModelSerializer
from django.http import Http404
from .models import (
    Product, ProductReview, ProductColor, ProductSize,
    ProductCategory, ProductImage,
)


class ProductCategorySerializer(ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ('id', 'name')


class ProductColorSerializer(ModelSerializer):
    class Meta:
        model = ProductColor
        fields = ('id', 'name')


class ProductSizeSerializer(ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ('id', 'name')


class ProductImageSerializer(ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt_text')


class ProductReviewSerializer(ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ('id', 'product', 'author', 'rating', 'comment', 'created_at')

    def save(self, **kwargs):
        user_id = self.context.get('user_id', None)
        if user_id is None:
            raise Http404('User not found')

        self.validated_data['author'] = user_id
        return super().save(**kwargs)


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'created_at', 'updated_at', 'name', 'category', 'gender',
                  'images', 'description', 'price', 'discount', 'price_with_discount')

    def to_representation(self, instance):
        many = self.context.get('many', None)
        representation = super().to_representation(instance)
        representation['images'] = ProductImageSerializer(instance.images.all(), many=True).data

        if many is False:
            representation['colors'] = ProductColorSerializer(instance.colors.all(), many=True).data
            representation['sizes'] = ProductSizeSerializer(instance.sizes.all(), many=True).data
            representation['comments'] = ProductReviewSerializer(instance.productreview_set.all(), many=True).data

        return representation
