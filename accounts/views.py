from django.shortcuts import render,redirect
from django.conf import settings
from django.http import JsonResponse
from rest_framework import status
from .models import CustomUser
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from .jwt import generateAccessToken, generateRefreshToken, saveRefreshToken
import requests

# Create your views here.
def kakao_login(request):
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
    redirect_uri = getattr(settings, 'KAKAO_CALLBACK_URI')
    authorize_url = f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={redirect_uri}&response_type=code&scope=account_email"
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
        
        email = profile_data.get('kakao_account', {}).get('email')
        nickname = profile_data.get('properties', {}).get('nickname')
        
        try:
            user = CustomUser.objects.get(email=email)
            user.is_social_user = True      
            user.social_provider = "Kakao"
            user.social_uid = profile_data.get('id')
            user.nickname = nickname
            user.save()
            
            
        except ObjectDoesNotExist:
            user = CustomUser.objects.create(email=email, is_social_user=True, social_provider="Kakao", social_uid=profile_data.get('id'))
        
        # user_id 값을 통해 access & refresh token 발급    
        user_id = user.id
        
        access_token = generateAccessToken(user_id)
        refresh_token = generateRefreshToken(user_id)
        expire_time = saveRefreshToken(user_id, refresh_token)  # redis에 refresh token 값 저장
        
        response_data = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expire_time' : expire_time
        }
        
        return JsonResponse(response_data)
    