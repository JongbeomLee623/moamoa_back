from django.urls import path, include
from accounts import views
from rest_framework import routers
from accounts.views import *

router = routers.DefaultRouter(trailing_slash=False)
router.register('user', UserViewSet)

urlpatterns = [
    path('kakao/login', views.kakao_login, name='kakao_login'),
    path('kakao/callback', views.kakao_callback, name='kakao_callback'),
    path('kakao/login/finish', views.KakaoLogin.as_view(), name='kakao_login_todjango'),
    path('kakao/logout', views.KakaoLogoutView.as_view(), name='kakao_logout'),
    path('', include(router.urls)),
]