from django.urls import path
from .views import (
    ProductViewSet, ReviewViewSet,
)

urlpatterns = [

    # Products
    path('products/', ProductViewSet.as_view({'get': 'list_products'})),
    path('product/<int:pk>/', ProductViewSet.as_view({'get': 'retrieve_product'})),

    # Reviews
    path('reviews/', ReviewViewSet.as_view({'get': 'list_reviews'})),
    path('review/', ReviewViewSet.as_view({'post': 'create_review'})),

]
