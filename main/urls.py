from django.urls import path
from . import views

urlpatterns = [
    path('get_cafe_info/', views.get_nearby_cafes, name='get_cafe_info'),

]