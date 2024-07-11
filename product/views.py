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
        operation_description="Retrieve a list of products with optional filters.",
        responses={200: ProductSerializer()},
        manual_parameters=[
            openapi.Parameter('q', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING),
            openapi.Parameter('gender_id', openapi.IN_QUERY, description="Gender ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('category_id', openapi.IN_QUERY, description="Category ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('color', openapi.IN_QUERY, description="Color name", type=openapi.TYPE_STRING),
            openapi.Parameter('size', openapi.IN_QUERY, description="Size name", type=openapi.TYPE_STRING),
            openapi.Parameter('min_price', openapi.IN_QUERY, description="Minimum price", type=openapi.TYPE_NUMBER,
                              format=openapi.FORMAT_FLOAT),
            openapi.Parameter('max_price', openapi.IN_QUERY, description="Maximum price", type=openapi.TYPE_NUMBER,
                              format=openapi.FORMAT_FLOAT),
        ],
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
        operation_description="Retrieve a specific product and its related products.",
        responses={
            200: openapi.Response(
                description="Product and related products retrieved successfully.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'product': openapi.Schema(
                            type=openapi.TYPE_OBJECT, properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                                'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                                'category': openapi.Schema(type=openapi.TYPE_STRING),
                                'gender': openapi.Schema(type=openapi.TYPE_STRING),
                                'images': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                         items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                                'description': openapi.Schema(type=openapi.TYPE_STRING),
                                'price': openapi.Schema(type=openapi.TYPE_NUMBER),
                                'discount': openapi.Schema(type=openapi.TYPE_NUMBER),
                                'price_with_discount': openapi.Schema(type=openapi.TYPE_NUMBER),
                                'colors': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                         items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                                'sizes': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                        items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                                'comments': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                           items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                            }),
                        'related_products': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'created_at': openapi.Schema(type=openapi.TYPE_STRING,
                                                             format=openapi.FORMAT_DATETIME),
                                'updated_at': openapi.Schema(type=openapi.TYPE_STRING,
                                                             format=openapi.FORMAT_DATETIME),
                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                                'category': openapi.Schema(type=openapi.TYPE_STRING),
                                'gender': openapi.Schema(type=openapi.TYPE_STRING),
                                'images': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                         items=openapi.Schema(
                                                             type=openapi.TYPE_OBJECT)),
                                'description': openapi.Schema(type=openapi.TYPE_STRING),
                                'price': openapi.Schema(type=openapi.TYPE_NUMBER),
                                'discount': openapi.Schema(type=openapi.TYPE_NUMBER),
                                'price_with_discount': openapi.Schema(
                                    type=openapi.TYPE_NUMBER),
                            })),
                    }
                )
            ),
            404: "Product not found",
        },
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="ID of the product.",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
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
        operation_description="Create a new product review.",
        request_body=ProductReviewSerializer,
        responses={
            201: openapi.Response(description="Review added successfully."),
            400: openapi.Response(description="Bad Request.")
        },
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="User's access token.",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
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
        operation_description="Retrieve a list of active product reviews.",
        responses={
            200: openapi.Response(
                description="List of active product reviews.",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'review': openapi.Schema(type=openapi.TYPE_STRING),
                        'rating': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                        # Add other fields here
                    })
                )
            ),
            400: openapi.Response(description="Bad Request.")
        },
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number.",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="Number of reviews per page.",
                type=openapi.TYPE_INTEGER
            ),
        ],
    )
    def list_reviews(self, request, *args, **kwargs):
        reviews = ProductReview.objects.filter(is_active=True).order_by('-created_at')
        serializer = ProductReviewSerializer(reviews)
        return Response(serializer.data, status=status.HTTP_200_OK)
