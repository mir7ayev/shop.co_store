import requests

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.utils import get_user_data
from .models import Product, ProductComment
from .serializers import ProductSerializer, ProductCommentSerializer


class ProductPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductViewSet(ViewSet):
    # permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Retrieve a list of products with optional filters and pagination.",
        responses={200: ProductSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('query', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING),
            openapi.Parameter('gender_id', openapi.IN_QUERY, description="Gender ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('category_id', openapi.IN_QUERY, description="Category ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('color', openapi.IN_QUERY, description="Color name", type=openapi.TYPE_STRING),
            openapi.Parameter('size', openapi.IN_QUERY, description="Size name", type=openapi.TYPE_STRING),
            openapi.Parameter('min_price', openapi.IN_QUERY, description="Minimum price", type=openapi.TYPE_NUMBER),
            openapi.Parameter('max_price', openapi.IN_QUERY, description="Maximum price", type=openapi.TYPE_NUMBER),
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page",
                              type=openapi.TYPE_INTEGER),
        ],
    )
    def list_products(self, request, *args, **kwargs):
        products = Product.objects.filter(is_available=True).order_by('-created_at')

        filters = {
            'query': request.query_params.get('q'),
            'gender_id': request.query_params.get('gender_id'),
            'category_id': request.query_params.get('category_id'),
            'color': request.query_params.get('color'),
            'size': request.query_params.get('size'),
            'min_price': request.query_params.get('min_price'),
            'max_price': request.query_params.get('max_price'),
        }

        if filters['query']:
            products = products.filter(name__icontains=filters['query'])
        if filters['gender_id']:
            products = products.filter(gender_id=filters['gender_id'])
        if filters['category_id']:
            products = products.filter(category_id=filters['category_id'])
        if filters['color']:
            products = products.filter(colors__name=filters['color'])
        if filters['size']:
            products = products.filter(sizes__name=filters['size'])
        if filters['min_price']:
            products = products.filter(price__gte=filters['min_price'])
        if filters['max_price']:
            products = products.filter(price__lte=filters['max_price'])

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
        product = get_object_or_404(Product, id=pk, is_available=True)
        product_serializer = ProductSerializer(product, context={'many': False})

        related_products = Product.objects.filter(is_available=True, category_id=product.category_id).exclude(id=pk)
        related_products_serializer = ProductSerializer(related_products, many=True)

        response_data = {
            'product': product_serializer.data,
            'related_products': related_products_serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)


class CommentViewSet(ViewSet):
    # permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Add a comment.",
        request_body=ProductCommentSerializer,
        responses={
            201: openapi.Response(description="Comment added"),
            400: openapi.Response(description="Invalid data")
        },
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="User access token",
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )
    def create_comment(self, request, *args, **kwargs):
        user_access_token = request.headers.get('Authorization')
        user_obj = get_user_data(user_access_token)
        user_id = user_obj.json().get('id')

        serializer = ProductCommentSerializer(data=request.data, context={'user_id': user_id})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Comment added"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Retrieve a list of active comments.",
        responses={200: ProductCommentSerializer(many=True)},
    )
    def list_comments(self, request, *args, **kwargs):
        comments = ProductComment.objects.filter(is_active=True).order_by('-created_at')
        serializer = ProductCommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
