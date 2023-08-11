import requests
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
    if "access_token" in token_req_json:
        access_token = token_req_json["access_token"]
        # Check if access token is expired
        if "expires_in" in token_req_json:
            expires_in = token_req_json["expires_in"]
            if expires_in <= 0:
                refresh_token = token_req_json.get("refresh_token")
                if refresh_token:
                    # Refresh the access token using the refresh token
                    refresh_req = requests.post(
                        f"https://kauth.kakao.com/oauth/token",
                        data={
                            "grant_type": "refresh_token",
                            "client_id": rest_api_key,
                            "refresh_token": refresh_token
                        }
                    )
                    refresh_req_json = refresh_req.json()
                    if "access_token" in refresh_req_json:
                        access_token = refresh_req_json["access_token"]
                    else:
                        return JsonResponse(
                            {'error': 'Failed to refresh access token'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
    

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
    email = kakao_account.get('email')

    # Handle Signup or Signin
    try:
        user = User.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생, 맞으면 로그인
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        if social_user.provider != 'kakao':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
        # 기존에 Kakao로 가입된 유저
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}/api/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)
    except User.DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입
        data = {'access_token': access_token, 'code': code}
        print(data)
        accept = requests.post(
            f"{BASE_URL}/api/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        print(accept_status)
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup ing'}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)
