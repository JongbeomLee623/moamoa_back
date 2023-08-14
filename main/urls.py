from django.urls import path, include
from . import views
from rest_framework import routers
from .views import StoreViewSet

store_router = routers.DefaultRouter(trailing_slash=False)
store_router.register('store', StoreViewSet, basename='store')


urlpatterns = [
    # path('get_cafe_info/', views.get_nearby_cafes, name='get_cafe_info'),
    # path('get-store-info/', StoreViewSet.getStore, name='get-store-info'),
    path('get-store/', views.add_menus_to_cafe, name='add_menus_to_cafe'),
    path('get-store/<int:store_id>/review', views.review_read_create, name='review_read_create'),
    path('get-store/<int:store_id>/review/<int:review_id>/', views.review_detail_update_delete, name='review_detail_update_delete'),
    path('get-store/<int:store_id>/board', views.board_read_create, name='board_read_create'),
    path('get-store/<int:store_id>/chat', views.chat_read_create, name='chat_read_create'),
    path('', include(store_router.urls)),
    path('get-store/<int:store_id>/wordcloud', views.generate_wordcloud, name='generate_wordcloud'),
]