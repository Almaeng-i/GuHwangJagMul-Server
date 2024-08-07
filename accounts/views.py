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
from GHJM.json_response_setting import JsonResponse
from django.views.decorators.http import require_http_methods
import requests

REFRESH_TOKEN = 'refreshtoken'

# Create your views here.
def kakao_login(request):
    access_token = request.headers.get("accesstoken")

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

    
require_http_methods(['POST'])
def reissue_token(request):
    refresh_token = request.headers.get(REFRESH_TOKEN)
    
    try:
        user_id = decode_token(refresh_token).get('user_id')
        
    except DecodeError:
        return JsonResponse({'error': '옳바르지 않은 리프레시 토큰 형식입니다.'}, status=401)
    
    except ExpiredSignatureError:
        return JsonResponse({'error': '리프레시 토큰이 만료되었습니다.'}, status=401)
    
    except InvalidTokenError:
        return JsonResponse({'error': '유효하지 않은 리프레시 토큰 입니다.'}, status=401)
    
    # user_id에 해당하는 토큰을 가지고옴.
    saved_refresh_token = cache.get(user_id)
    
    if saved_refresh_token != None:
        access_token = generate_access_token(user_id)
        refresh_token = generate_refresh_token(user_id)
        access_expire_time_format = get_token_exp_in_str_format(access_token)
        
        response_data = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'access_expire_time': access_expire_time_format
        }

        return JsonResponse(response_data)


@require_http_methods(['DELETE'])
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
    
    return JsonResponse({'message': '로그아웃 되었습니다.'}, status=204)


@require_http_methods(['DELETE'])
def delete_user(request):
    user = request.user
    user.delete()
    
    return JsonResponse({'Success': '회원탈퇴가 완료되었습니다.'})
