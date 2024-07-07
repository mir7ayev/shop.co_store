from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('/api/v1/', include('product.urls')),
    # path('/api/v1/cart/', include('cart.urls')),
    # path('/api/v1/order/', include('order.urls')),
    # path('/api/v1/core/', include('core.urls')),
]
