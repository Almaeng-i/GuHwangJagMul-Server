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
    return redirect(f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={settings.KAKAO_CALLBACK_URI}&response_type=code")
    
def kakao_callback(request):
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
    code = request.GET.get("code")
    redirect_uri = f"{settings.SERVER_BASE_URL}accounts/login/kakao/callback"
    
    
    # Access Token Request
    token_res = requests.get(f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={rest_api_key}&redirect_uri={redirect_uri}&code={code}")
    token_res_json = token_res.json()
    error = token_res_json.get("error")
    
    if error is not None:
        raise JSONDecodeError(error)
    
    access_token = token_res_json.get("access_token")

    # Email Request
    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"})
    profile_json = profile_request.json()
    kakao_account = profile_json.get('kakao_account')
    
    """
    kakao_account에서 이메일 외에
    카카오톡 프로필 이미지, 배경 이미지 url 가져올 수 있음
    """
    email = kakao_account.get('email')
    
    """
    회원가입 or 로그인 Request
    """
    try:
        user = CustomUser.objects.get(email=email)
        
        # 다른 SNS로 가입된 유저인지 판별하기 위함.
        social_user = SocialAccount.objects.get(user=user)
        
        # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생, 맞으면 로그인
        if social_user is None:
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        
        if social_user.provider != 'kakao':
            return JsonResponse({'err_msg': 'no matching socialtype'}, status=status.HTTP_400_BAD_REQUEST)

        # 기존에 kakao로 가입된 유저
        data = {'access_token': access_token, 'code': code}
        
        # 카카오 서버로 data에 저장된 액세스 토큰,코드값을 Post 요청으로 보내고
        # 해당 요청이 성공할 경우 사용자에 대한 정보값을 accept에 저장
        accept = requests.post(
            f"{settings.SERVER_BASE_URL}accounts/kakao/login/finish/", data=data)
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
            f"{settings.SERVER_BASE_URL}accounts/kakao/login/finish/", data=data)
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