from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model
from django.http import Http404
from .models import (
    Product, ProductComment, ProductColor, ProductSize,
)

User = get_user_model()


# TODO: get user from other micro-service

class ProductColorSerializer(ModelSerializer):
    class Meta:
        model = ProductColor
        fields = '__all__'


class ProductSizeSerializer(ModelSerializer):
    class Meta:
        model = ProductSize
        fields = '__all__'


class ProductCommentSerializer(ModelSerializer):
    class Meta:
        model = ProductComment
        fields = '__all__'

    def save(self, **kwargs):
        request = self.context.get('request', None)

        user = User.objects.filter(user_id=request.user.id).first()
        if user is None:
            raise Http404('User not found')

        self.validated_data['author'] = user

        return super().save(**kwargs)


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'created_at', 'updated_at', 'name', 'category', 'gender',
                  'image', 'description', 'price', 'discount', 'price_with_discount')

    def to_representation(self, instance):
        many = self.context.get('many', None)
        representation = super().to_representation(instance)

        if many is False:
            representation['colors'] = ProductColorSerializer(instance.colors.all(), many=True).data
            representation['sizes'] = ProductSizeSerializer(instance.sizes.all(), many=True).data
            representation['comments'] = ProductCommentSerializer(instance.productcomment_set.all(), many=True).data

        return representation
