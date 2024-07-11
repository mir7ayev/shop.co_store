from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="Blog Analytics",
        default_version='v1',
        description="API documentation for Blog Analytics",
    ),
    permission_classes=[AllowAny, ],
    public=True,
)

urlpatterns = [

    # Custom URLs
    path('admin/', admin.site.urls),
    path('api/v1/', include('product.urls')),
    # path('/api/v1/cart/', include('cart.urls')),
    # path('/api/v1/order/', include('order.urls')),
    # path('/api/v1/core/', include('core.urls')),

    # Swagger URLs
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),

    # Static and Media URLs
    re_path(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT})

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
