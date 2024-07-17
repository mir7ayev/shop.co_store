from django.urls import path
from .views import (
    ProductViewSet, CommentViewSet,
)

urlpatterns = [

    # Products
    path('products/', ProductViewSet.as_view({'get': 'list_products'})),
    path('product/<int:pk>/', ProductViewSet.as_view({'get': 'retrieve_product'})),
    path('rate-product/', ProductViewSet.as_view({'post': 'rate_product'})),

    # Comments
    path('comments/', CommentViewSet.as_view({'get': 'list_comments'})),
    path('comment/', CommentViewSet.as_view({'post': 'create_comment'})),

]
