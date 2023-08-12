from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import jwt
import time
from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header
from .models import User

class CookieAuthentication(BaseAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')

        if not access_token:
            return None
        
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])

        expire = payload.get('exp')

        if expire < time.time():
            raise None
        
        user_id = payload.get('user_id')
        if not user_id:
            raise None
        
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('No such user')
        
        return (user, None)
