import requests
from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.response import Response
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialAccount
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from rest_framework.decorators import api_view, permission_classes, action, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from django.utils import timezone
from main.models import Store
from .serializers import UserSerializer
import math
from rest_framework.views import APIView
from django.contrib.auth import logout
from main.serializers import *
from main.models import *

from rest_framework import viewsets
from rest_framework import serializers

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect

from .authentication import CookieAuthentication

BASE_URL = 'http://13.209.111.199'
KAKAO_CALLBACK_URI = BASE_URL + '/api/kakao/callback'
# KAKAO_CALLBACK_URI = 'http://localhost:5173/App/Mainpage'

class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = KAKAO_CALLBACK_URI


@csrf_exempt
def kakao_login(request):
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code"
    )

def kakao_callback(request):
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
    code = request.GET.get("code")
    redirect_uri = KAKAO_CALLBACK_URI

    # Access Token Request
    token_req = requests.post(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={rest_api_key}&redirect_uri={redirect_uri}&code={code}"
    )
    token_req_json = token_req.json()

    error = token_req_json.get("error")
    if error is not None:
        return JsonResponse({'error': error}, status=status.HTTP_400_BAD_REQUEST)
    access_token = token_req_json.get('access_token')
    
    # Get User Profile
    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    profile_json = profile_request.json()

    #print(kakao_account)
    error = profile_json.get("error")
    if error is not None:
        return JsonResponse({'error': error}, status=status.HTTP_400_BAD_REQUEST)
    kakao_account = profile_json.get('kakao_account')
    profile = kakao_account.get('profile')
    nickname = profile.get('nickname')
    image_url = profile.get('profile_image_url')
    user_id = "kakao_" + nickname + "_" + str(profile_json.get('id'))

    # Signup or Signin
    try:
        user = User.objects.get(username=user_id)
        # 기존 사용자의 경우
        social_user = SocialAccount.objects.get(user=user)
        if social_user.provider != 'kakao':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}/api/kakao/login/finish", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
        
    except User.DoesNotExist:
        # 새로운 사용자의 경우
        user = User.objects.create_user(username=user_id, password=None)

        user.nickname = nickname  # Set nickname
        user.image_url = image_url  # Set image URL
        user.save()

        social_user = SocialAccount.objects.create(user=user, provider='kakao', uid=str(profile_json.get('id')), extra_data=profile_json)

        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}/api/kakao/login/finish", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        
    refresh_token = RefreshToken.for_user(user)
    access_token = str(refresh_token.access_token)
    
    #frontend_redirect_uri = 'http://localhost:5173/App/Mainpage',
    #frontend_redirect_uri = 'http://13.209.178.19:5173/App/Mainpage'
    #frontend_redirect_uri = 'http://13.209.111.199:5173/App/Mainpage'
    
    frontend_redirect_uri = 'http://127.0.0.1:5173/App/Mainpage'
    response = redirect(frontend_redirect_uri)
    response.set_cookie('access_token', access_token, max_age=36000, httponly=True)
    
    return response

# class KakaoLogoutView(APIView):
#     def post(self, request):
#         # 카카오 토큰을 만료시키는 API 호출
#         # access_token = request.COOKIES.get('access_token')
#         # kakao_token = request.data.get('kakao_token')
#         rest_api_key = getattr(settings, 'KAKAO_APP_ADMIN_KEY')
#         if rest_api_key:
#             kakao_response = requests.post('https://kapi.kakao.com/v1/user/logout', headers={
#                 'Authorization': f'KakaoAK {rest_api_key}'
#             }, data={
#                 'target_id_type': 'user_id',
#                 'target_id': request.user.socialaccount_set.get(provider='kakao').uid
#             })
#             if kakao_response.status_code == 200:
#                 # 카카오 토큰 만료 성공
#                 # headers의 cookie 에 담긴 access token 만료
#                 response = HttpResponse(status=status.HTTP_200_OK)
#                 response.delete_cookie('access_token')
#                 logout(request)


#                 return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
        
#         return Response({'message': 'Invalid Kakao token.'}, status=status.HTTP_400_BAD_REQUEST)

class KakaoLogoutView(APIView):
    def post(self, request):
        rest_api_key = getattr(settings, 'KAKAO_APP_ADMIN_KEY')
        if rest_api_key:
            user = request.user
            if user:
                kakao_uid = user.socialaccount_set.get(provider='kakao').uid
                print(kakao_uid)
                kakao_response = requests.post('https://kapi.kakao.com/v1/user/logout', headers={
                    'Authorization': f'KakaoAK {rest_api_key}'
                }, data={
                    'target_id_type': 'user_id',
                    'target_id': kakao_uid
                })
                if kakao_response.status_code == 200:
                    # 카카오 토큰 만료 성공
                    response = Response({'message': 'Kakao logout successful.'}, status=status.HTTP_200_OK)
                    response.delete_cookie('access_token')
                    return response
        return Response({'message': 'Invalid Kakao token.'}, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [CookieAuthentication]  # CookieAuthentication 적용
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def current_user(self, request):
        user_serializer = self.serializer_class(request.user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'])
    def scraps(self, request):
        user = request.user
        scraps = Scrap.objects.filter(user=user)
        store_list = [scrap.store for scrap in scraps]
        serializer = StoreSerializer(store_list, many=True, context={'scraps_action': True})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def my_reviews(self, request):
        user = request.user
        reviews = Review.objects.filter(user=user)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)