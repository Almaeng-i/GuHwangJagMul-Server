from django.shortcuts import render,redirect
from django.conf import settings
from django.http import JsonResponse
from rest_framework import status
from .models import CustomUser
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from jwt import DecodeError, ExpiredSignatureError, InvalidTokenError
from .jwt import generate_access_token, generate_refresh_token, decode_token, get_token_exp,save_refresh_token, get_token_exp_in_str_format
from .json_response_setting import JsonResponse
import requests

REFRESH_TOKEN = 'refresh-token'

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
        
        # access & refresh token 발급 후 redis에 expire date 저장 
        access_token = generate_access_token(user_id)
        refresh_token = generate_refresh_token(user_id)
        access_expire_time_format = get_token_exp_in_str_format(access_token)
        refresh_expire_time_format = get_token_exp_in_str_format(refresh_token)
        save_refresh_token(user_id, refresh_token)
        
        response_data = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'access_expire_time': access_expire_time_format,
            'refresh_expire_time' : refresh_expire_time_format
        }
        return JsonResponse(response_data)

    

def reissue_token(request):
    refresh_token = request.headers.get(REFRESH_TOKEN)
    
    try:
        user_id = decode_token(refresh_token).get('user_id')
    
    except DecodeError:
        return JsonResponse({'error': '옳바르지 않은 토큰 형식입니다.'}, status=401)
    
    except ExpiredSignatureError:
        return JsonResponse({'error': '토큰이 만료되었습니다.'}, status=401)
    
    except InvalidTokenError:
        return JsonResponse({'error': '유효하지 않은 토큰 입니다.'}, status=401)
    
    # user_id에 해당하는 토큰을 가지고옴.
    saved_refresh_token = cache.get(user_id)
    
    if saved_refresh_token != None:
        access_token = generate_access_token(user_id)
        
        access_expire_time_format = get_token_exp_in_str_format(access_token)
        
        response_data = {
            'access_token': access_token,
            'access_expire_time': access_expire_time_format
        }

        return JsonResponse(response_data)


# user가 로그아웃 버튼을 직접 클릭 했을 경우    
def logout(request):
    refresh_token = request.headers.get(REFRESH_TOKEN)
     
    try:
        user_id = decode_token(refresh_token).get('user_id')
    
    except DecodeError:
        return JsonResponse({'error': '옳바르지 않은 토큰 형식입니다.'}, status=401)
    
    except ExpiredSignatureError:
        return JsonResponse({'error': '토큰이 만료되었습니다.'}, status=401)
    
    except InvalidTokenError:
        return JsonResponse({'error': '유효하지 않은 토큰 입니다.'}, status=401)
    
    # user_id에 해당하는 refresh token을 redis에서 삭제
    cache.delete(user_id)
    
    return JsonResponse({'message': '로그아웃 되었습니다.'})
