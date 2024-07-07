from django.shortcuts import render
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
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

    def update_product(self, request, *args, **kwargs):
        pk = kwargs.get('pk')

        product = Product.objects.filter(id=pk, is_available=True).first()
        if product is None:
            return Response("Product not found", status=status.HTTP_404_NOT_FOUND)

        partial = request.method == 'PATCH'

        serializer = ProductSerializer(product, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def related_products(self, request, *args, **kwargs):
        pk = kwargs.get('pk')

        product = Product.objects.filter(id=pk, is_available=True).first()
        if product is None:
            return Response("Product not found", status=status.HTTP_404_NOT_FOUND)

        related_products = Product.objects.filter(is_available=True,
                                                  category_id=product.category_id).exclude(id=pk)
        serializer = ProductSerializer(related_products)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def search_products(self, request):
        query_params = request.query_params
        product_name = query_params.get('name')
        category_id = query_params.get('category_id')

        products = Product.objects.filter(is_available=True)
        if product_name is not None:
            products = products.filter(name__icontains=product_name)

        if category_id is not None:
            products = products.filter(category_id=category_id)

        serializer = ProductSerializer(products, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def best_seller_products(self, request, *args, **kwargs):
        pass

    def filter_products(self, request, *args, **kwargs):
        pass


class CommentViewSet(ViewSet):
    permission_classes = (IsAuthenticated,)

    def create_comment(self, request, *args, **kwargs):
        serializer = ProductCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("Comment added", status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list_comments(self, request, *args, **kwargs):
        comments = ProductComment.objects.filter(is_active=True)
        serializer = ProductCommentSerializer(comments)

        return Response(serializer.data, status=status.HTTP_200_OK)
