from django.shortcuts import render
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import (
    Product, ProductComment,
)
from .serializers import (
    ProductSerializer, ProductCommentSerializer,
)


class ProductPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductViewSet(ViewSet):
    permission_classes = (IsAuthenticated,)

    def list_products(self, request, *args, **kwargs):
        products = Product.objects.filter(is_available=True)

        gender_id = request.GET.get('gender_id')
        if gender_id is not None:
            products = products.filter(is_available=True, gender_id=gender_id)

        category_id = request.GET.get('category_id')
        if category_id is not None:
            products = products.filter(category_id=category_id, is_available=True)

        paginator = ProductPagination()
        paginated_products = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(paginated_products, many=True)

        return Response(data=paginator.get_paginated_response(serializer.data), status=status.HTTP_200_OK)

    def retrieve_product(self, request, *args, **kwargs):
        pk = kwargs.get('pk')

        product = Product.objects.filter(id=pk, is_available=True).first()
        if product is None:
            return Response("Product not found", status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, many=False)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def related_products(self, request, *args, **kwargs):
        pk = kwargs.get('pk')

        product = Product.objects.filter(id=pk, is_available=True).first()
        if product is None:
            return Response("Product not found", status=status.HTTP_404_NOT_FOUND)

        related_products = Product.objects.filter(is_available=True,
                                                  category_id=product.category_id).exclude(id=pk)
        serializer = ProductSerializer(related_products)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def filter_products(self, request, *args, **kwargs):
        pass

    def search_products(self, request, *args, **kwargs):
        pass


class CommentViewSet(ViewSet):
    permission_classes = (IsAuthenticated,)

    def create_comment(self, request, *args, **kwargs):
        pass

    def list_comments(self, request, *args, **kwargs):
        pass
