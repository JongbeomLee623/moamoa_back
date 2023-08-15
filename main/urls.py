from django.urls import path, include
from . import views
from rest_framework import routers
from .views import StoreViewSet
from django.conf import settings
from django.conf.urls.static import static


store_router = routers.DefaultRouter(trailing_slash=False)
store_router.register('store', StoreViewSet, basename='store')


urlpatterns = [
    path('get-store/<int:store_id>/review', views.review_read_create, name='review_read_create'),
    path('get-store/<int:store_id>/review/<int:review_id>/', views.review_detail_update_delete, name='review_detail_update_delete'),
    path('get-store/<int:store_id>/board', views.board_read_create, name='board_read_create'),
    path('get-store/<int:store_id>/chat', views.chat_read_create, name='chat_read_create'),
    path('get-store/<int:store_id>/wordcloud', views.generate_wordcloud, name='generate_wordcloud'),
    path('', include(store_router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)