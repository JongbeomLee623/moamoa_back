import requests
import json
from django.shortcuts import redirect
from django.conf import settings
from django.http import JsonResponse
from json.decoder import JSONDecodeError
from rest_framework import status
from rest_framework.response import Response
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialAccount
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

BASE_URL = 'http://localhost:8000'
KAKAO_CALLBACK_URI = BASE_URL + '/api/kakao/callback/'


class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = KAKAO_CALLBACK_URI

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
    print(profile_json)
    #print(kakao_account)
    error = profile_json.get("error")
    if error is not None:
        return JsonResponse({'error': error}, status=status.HTTP_400_BAD_REQUEST)
    kakao_account = profile_json.get('kakao_account')
    profile = kakao_account.get('profile')
    nickname = profile.get('nickname')

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
            f"{BASE_URL}/api/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
        
    except User.DoesNotExist:
        # 새로운 사용자의 경우
        user = User.objects.create_user(username=user_id, password=None)
        social_user = SocialAccount.objects.create(user=user, provider='kakao', uid=str(profile_json.get('id')), extra_data=profile_json)

        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}/api/kakao/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        
    refresh_token = RefreshToken.for_user(user)
    access_token = str(refresh_token.access_token)
    response_data = {
            "message": "Login Susccess",
            "access_token": access_token,
            "refresh_token": str(refresh_token),
        }
    return JsonResponse(response_data)
