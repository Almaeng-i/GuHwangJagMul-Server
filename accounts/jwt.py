from django.conf import settings
from datetime import datetime, timedelta
from django.core.cache import cache
import jwt

Access = 'AccessToken'
Refresh = 'RefreshToken'

def generateAccessToken(user_id):
    # JWT payload로 claim 설정
    payload = {
        'user_id': user_id,
        'exp': datetime.now() + timedelta(days=1),  # 토큰 만료 시간 설정
        'type': Access
    }

    # JWT 토큰 생성
    jwt_token = jwt.encode(payload, getattr(settings, 'SECRET_KEY'), algorithm='HS256')

    return jwt_token

def generateRefreshToken(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.now() + timedelta(days=1),  # 토큰 만료 시간 설정
        'type': Refresh
    }

    # JWT 토큰 생성
    jwt_token = jwt.encode(payload, getattr(settings, 'SECRET_KEY'), algorithm='HS256')

    return jwt_token 
   

def saveRefreshToken(user_id, refresh_token):
    cache_key = user_id
    cache_value = refresh_token
    expire_time = getattr(settings, "REFRESH_EXPIRE_TIME")
    
    cache.set(key=cache_key, value=cache_value, timeout=expire_time)      # redis에 저장
   
    