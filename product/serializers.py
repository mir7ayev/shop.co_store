from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.http import Http404
from .models import (
    Product, ProductComment, ProductColor, ProductSize,
    ProductCategory, ProductImage, ProductColorQuantity,
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
        fields = ('id', 'image')


class ProductColorQuantitySerializer(ModelSerializer):
    color_name = serializers.CharField(source='color.name', read_only=True)
    images = ProductImageSerializer(many=True)

    class Meta:
        model = ProductColorQuantity
        fields = ('color', 'color_name', 'quantity', 'images')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['images'] = [image.image.url for image in instance.images.all()]
        return representation


class ProductCommentSerializer(ModelSerializer):
    class Meta:
        model = ProductComment
        fields = ('id', 'product', 'author', 'comment', 'created_at')

    def save(self, **kwargs):
        user_id = self.context.get('user_id', None)
        if user_id is None:
            raise Http404('User not found')

        self.validated_data['author'] = user_id
        return super().save(**kwargs)


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'created_at', 'updated_at', 'name', 'category', 'gender', 'description',
                  'price', 'discount', 'price_with_discount', 'is_available')

    def to_representation(self, instance):
        many = self.context.get('many', None)
        representation = super().to_representation(instance)
        representation['colors'] = ProductColorQuantitySerializer(instance.productcolorquantity_set.all(),
                                                                  many=True).data

        if many is False:
            representation['sizes'] = ProductSizeSerializer(instance.sizes.all(), many=True).data
            representation['comments'] = ProductCommentSerializer(instance.productcomment_set.all(), many=True).data

        return representation
