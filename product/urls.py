from django.urls import path
from .views import (
    ProductViewSet, CommentViewSet,
)

urlpatterns = [

    # Products
    path('products/', ProductViewSet.as_view({'get': 'list_products'})),
    path('product/<int:pk>/', ProductViewSet.as_view({'get': 'retrieve_product'})),
    path('related_products/<int:pk>/', ProductViewSet.as_view({'get': 'related_products'})),
    path('products/search/', ProductViewSet.as_view({'get': 'search_products'})),

    # Comments
    path('comments/', CommentViewSet.as_view({'get': 'list_comments'})),
    path('comment/', CommentViewSet.as_view({'post': 'create_comment'})),

]
