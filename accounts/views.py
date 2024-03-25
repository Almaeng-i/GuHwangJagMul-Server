from django.shortcuts import render,redirect
from django.conf import settings
from accounts.models import CustomUser
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.kakao import views as kakao_view
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.http import JsonResponse
from rest_framework import status
from json.decoder import JSONDecodeError
import requests

# Create your views here.
def kakao_login(request):
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
    # redirect_uri = 'http://localhost:8000/accounts/login/kakao/callback'
    # redirect_params = {
    #     'client_id': rest_api_key,
    #     'redirect_uri': redirect_uri,
    #     'response_type': 'code'
    # }
    # redirect_url = f"https://kauth.kakao.com/oauth/authorize?{urlencode(redirect_params)}
    # return redirect(redirect_url)
    
    # 원래 참고하던 doc에서 사용하는 코드
    return redirect(f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={settings.KAKAO_CALLBACK_URI}&response_type=code")
    
def kakao_callback(request):
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
    code = request.GET.get("code")
    redirect_uri = 'http://localhost:8000/accounts/login/kakao/callback'
    """
    Access Token Request
    """
    token_req = requests.get(f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={rest_api_key}&redirect_uri={redirect_uri}&code={code}")
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    
    if error is not None:
        raise JSONDecodeError(error)
    
    access_token = token_req_json.get("access_token")

    """
    Email Request
    """
    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"})
    profile_json = profile_request.json()
    kakao_account = profile_json.get('kakao_account')
    
    """
    kakao_account에서 이메일 외에
    카카오톡 프로필 이미지, 배경 이미지 url 가져올 수 있음
    print(kakao_account) 참고
    """
    # print(kakao_account)
    email = kakao_account.get('email')
    
    """
    Signup or Signin Request
    """
    try:
        user = CustomUser.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생, 맞으면 로그인
        # 다른 SNS로 가입된 유저
        social_user = SocialAccount.objects.get(user=user)
        
        if social_user is None:
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        
        if social_user.provider != 'kakao':
            return JsonResponse({'err_msg': 'no matching socialtype'}, status=status.HTTP_400_BAD_REQUEST)

        # 기존에 kakao로 가입된 유저
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{settings.BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
        
        accept_json = accept.json()
        accept_json.pop('user', None)
        
        return JsonResponse(accept_json)
    
    except CustomUser.DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{settings.BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        
        # user의 pk, email, first name, last name과 Access Token, Refresh token 가져옴
        accept_json = accept.json()
        accept_json.pop('user', None)
        
        return JsonResponse(accept_json)
    
class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = settings.KAKAO_CALLBACK_URI