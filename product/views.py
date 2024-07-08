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
            products = products.filter(gender_id=gender_id)

        category_id = request.GET.get('category_id')
        if category_id is not None:
            products = products.filter(category_id=category_id)

        color = request.GET.get('color')
        if color is not None:
            products = products.filter(colors__name=color)

        size = request.GET.get('size')
        if size is not None:
            products = products.filter(sizes__name=size)

        min_price = request.GET.get('min_price')
        if min_price is not None:
            products = products.filter(price__gte=min_price)

        max_price = request.GET.get('max_price')
        if max_price is not None:
            products = products.filter(price__lte=max_price)

        paginator = ProductPagination()
        paginated_products = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(paginated_products, many=True)

        return paginator.get_paginated_response(serializer.data)

    def retrieve_product(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        product = get_object_or_404(Product, id=pk, is_available=True)
        serializer = ProductSerializer(product, many=False, context={'many': False})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def related_products(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        product = get_object_or_404(Product, id=pk, is_available=True)
        related_products = Product.objects.filter(is_available=True, category_id=product.category_id).exclude(id=pk)
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

    # TODO: RANKED PRODUCTS (HOT)


class CommentViewSet(ViewSet):
    permission_classes = (IsAuthenticated,)

    def create_comment(self, request, *args, **kwargs):
        serializer = ProductCommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response("Comment added", status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list_comments(self, request, *args, **kwargs):
        comments = ProductComment.objects.filter(is_active=True)
        serializer = ProductCommentSerializer(comments)

        return Response(serializer.data, status=status.HTTP_200_OK)
