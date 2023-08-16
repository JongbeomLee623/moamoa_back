from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from main.serializers import *
from main.models import *

class CustomTokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh_token'])
        data = {'access_token': str(refresh.access_token)}

        return data
    
class UserSerializer(serializers.ModelSerializer):
    # reviews = serializers.SerializerMethodField()

    # def get_reviews(self, instacnce):
    #     reviews = Review.object.filter(user=instacnce)
    #     serializer = ReviewSerializer(reviews, many=True)
    #     return serializer.data

    class Meta:
        model = User
        fields = "__all__"