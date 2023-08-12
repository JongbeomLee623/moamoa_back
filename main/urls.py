from django.urls import path, include
from . import views
from rest_framework import routers
from .views import StoreViewSet

store_router = routers.DefaultRouter(trailing_slash=False)
store_router.register('store', StoreViewSet)


urlpatterns = [
    # path('get_cafe_info/', views.get_nearby_cafes, name='get_cafe_info'),
    # path('get-store-info/', StoreViewSet.getStore, name='get-store-info'),
    path('', include(store_router.urls)),
]