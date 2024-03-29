from django.shortcuts import render,redirect
from django.conf import settings
from allauth.socialaccount.providers.kakao import views as kakao_view
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.http import JsonResponse
from rest_framework import status

from django.views import View
import requests

# Create your views here.
def kakao_login(request):
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
    redirect_uri = getattr(settings, 'KAKAO_CALLBACK_URI')
    authorize_url = f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={redirect_uri}&response_type=code"
    return redirect(authorize_url) 

class KakaoCallbackView(View):
    def get(self, request):
        rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
        redirect_uri = getattr(settings, 'KAKAO_CALLBACK_URI')
        code = request.GET.get("code")
        
         # Access Token Request
        token_url = f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={rest_api_key}&redirect_uri={redirect_uri}&code={code}"
     
        token_response = requests.post(token_url)
        token_data = token_response.json()
        
        if 'error' in token_data:
            return JsonResponse({'error': token_data['error']}, status=status.HTTP_400_BAD_REQUEST)
        
        access_token = token_data.get("access_token")

        # Email Request
        profile_url = "https://kapi.kakao.com/v2/user/me"
        headers = {'Authorization' : f'Bearer {access_token}'}
        profile_response = requests.get(profile_url, headers=headers)
        profile_data = profile_response.json()
        
        return JsonResponse(profile_data)
    
    
class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = settings.KAKAO_CALLBACK_URI
