from django.urls import path
from .views import (
    ProductViewSet, CommentViewSet, MicroServiceViewSet,
)

urlpatterns = [

    # Products
    path('products/', ProductViewSet.as_view({'get': 'list_products'})),
    path('product/<int:pk>/', ProductViewSet.as_view({'get': 'retrieve_product'})),
    path('rate-product/', ProductViewSet.as_view({'post': 'rate_product'})),

    # Comments
    path('comments/', CommentViewSet.as_view({'get': 'list_comments'})),
    path('comment/', CommentViewSet.as_view({'post': 'create_comment'})),

    # Micro Service
    path('get-products/', MicroServiceViewSet.as_view({'get': 'get_products'})),

]
