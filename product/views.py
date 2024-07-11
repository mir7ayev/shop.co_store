import requests

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from django.shortcuts import get_object_or_404
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.utils import get_service_access_token, get_user_data

from .models import (
    Product, ProductReview,
)
from .serializers import (
    ProductSerializer, ProductReviewSerializer,
)


# TODO: RANKED PRODUCTS (HOT, POPULAR, NEW, BEST SELLER)
# TODO: DO COMMENT CREATE API REQUEST URLS
# TODO: ADD REVIEW (LOGIC)


class ProductPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductViewSet(ViewSet):
    # permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="List products",
        operation_summary="Get all products (by filter, search query) with pagination",
        responses={200: ProductSerializer()},
        manual_parameters=[
            openapi.Parameter('q', openapi.IN_QUERY, description='Query string',
                              type=openapi.TYPE_STRING),
            openapi.Parameter('gender_id', openapi.IN_QUERY, description='Filter by gender ID',
                              type=openapi.TYPE_INTEGER),
            openapi.Parameter('category_id', openapi.IN_QUERY, description='Filter by category ID',
                              type=openapi.TYPE_INTEGER),
            openapi.Parameter('color', openapi.IN_QUERY, description='Filter by color',
                              type=openapi.TYPE_STRING),
            openapi.Parameter('size', openapi.IN_QUERY, description='Filter by size',
                              type=openapi.TYPE_STRING),
            openapi.Parameter('min_price', openapi.IN_QUERY, description='Filter by minimum price',
                              type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT),
            openapi.Parameter('max_price', openapi.IN_QUERY, description='Filter by maximum price',
                              type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT),
            openapi.Parameter('page', openapi.IN_QUERY, description='Page number for pagination',
                              type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description='Number of results per page',
                              type=openapi.TYPE_INTEGER)
        ],
        tags=['products']
    )
    def list_products(self, request, *args, **kwargs):
        products = Product.objects.filter(is_available=True).order_by('-created_at')

        query = request.query_params.get('q')
        if query is not None:
            products = products.filter(name__icontains=query)

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

    @swagger_auto_schema(
        operation_description="Retrieve a product by ID and get related products in the same category",
        operation_summary="Get product details and related products",
        responses={200: ProductSerializer()},
        manual_parameters=[
            openapi.Parameter('pk', openapi.IN_PATH, description='Primary key of the product',
                              type=openapi.TYPE_INTEGER)
        ],
        tags=['product']
    )
    def retrieve_product(self, request, *args, **kwargs):
        pk = kwargs.get('pk')

        # Retrieve the main product
        product = get_object_or_404(Product, id=pk, is_available=True)
        product_serializer = ProductSerializer(product, many=False, context={'many': False})

        # Retrieve related products
        product_obj = Product.objects.filter(is_available=True, category_id=product.category_id).exclude(id=pk)
        related_products = product_obj.filter(name__icontains=product.name)
        related_products_serializer = ProductSerializer(related_products, many=True)

        # Combine both responses
        response_data = {
            'product': product_serializer.data,
            'related_products': related_products_serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)


class ReviewViewSet(ViewSet):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Create a new review on a product",
        operation_summary="Add a review",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'review': openapi.Schema(type=openapi.TYPE_STRING,
                                         description='review text'),
                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                             description='ID of the product being reviewed on'),
            },
            required=['review', 'product_id']
        ),
        responses={
            201: openapi.Response(description="Review added"),
            400: openapi.Response(description="Invalid data"),
            401: openapi.Response(description="Unauthorized"),
            500: openapi.Response(description="Internal server error")
        },
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="User's access token",
                              type=openapi.TYPE_STRING, required=True)
        ],
        tags=['reviews']
    )
    def create_review(self, request, *args, **kwargs):
        user_access_token = request.headers.get('Authorization')
        user_obj = get_user_data(user_access_token)
        user_id = user_obj.json().get('id')

        serializer = ProductReviewSerializer(data=request.data, context={'user_id': user_id})
        if serializer.is_valid():
            serializer.save()
            return Response("Review added", status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="List all active reviews",
        operation_summary="Get all active reviews",
        responses={200: ProductSerializer()},
        tags=['reviews']
    )
    def list_reviews(self, request, *args, **kwargs):
        reviews = ProductReview.objects.filter(is_active=True).order_by('-created_at')
        serializer = ProductReviewSerializer(reviews)
        return Response(serializer.data, status=status.HTTP_200_OK)
