from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model
from django.http import Http404
from .models import (
    Product, ProductComment,
)

User = get_user_model()


# TODO: get user from other micro-service

class ProductCommentSerializer(ModelSerializer):
    class Meta:
        model = ProductComment
        fields = '__all__'

    def save(self, **kwargs):
        request = self.context['request']
        user = User.objects.filter(user_id=request.user.id).first()

        if user is None:
            raise Http404('User not found')

        self.validated_data['author'] = user

        return super().save(**kwargs)


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['comments'] = ProductCommentSerializer(ProductComment.objects.filter(movie_id=instance.id),
                                                              many=True).data
