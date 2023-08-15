from django.urls import path, include
from . import views
from rest_framework import routers
from .views import *
from django.conf import settings
from django.conf.urls.static import static


store_router = routers.DefaultRouter(trailing_slash=False)
store_router.register('store', StoreViewSet, basename='store')

review_router = routers.DefaultRouter(trailing_slash=False)
review_router.register('review', ReviewViewSet, basename='review')

store_review_router = routers.DefaultRouter(trailing_slash=False)
store_review_router.register('review', StoreReviewViewSet, basename='store_review')


urlpatterns = [
    path('store/<int:store_id>/board', views.board_read_create, name='board_read_create'),
    path('store/<int:store_id>/chat', views.chat_read_create, name='chat_read_create'),
    path('store/<int:store_id>/wordcloud', views.generate_wordcloud, name='generate_wordcloud'),
    path('', include(store_router.urls)),
    path('', include(review_router.urls)),
    path('store/<int:store_id>/', include(store_review_router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)