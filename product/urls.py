from django.urls import path
from .views import (
    ProductViewSet,
)

urlpatterns = [

    # Products
    path('products/', ProductViewSet.as_view({'get': 'list_products'})),
    path('product/<int:pk>/', ProductViewSet.as_view({'get': 'retrieve_product'})),
    path('related/<int:pk>/', ProductViewSet.as_view({'get': 'related_products'})),

]
