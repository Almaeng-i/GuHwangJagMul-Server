from django.conf import settings
from datetime import datetime, timedelta
from django.core.cache import cache
import jwt

access = 'AccessToken'
refresh = 'RefreshToken'
algorithm = getattr(settings, 'ALGORITHM')

def generateAccessToken(user_id):
    # JWT payload로 claim 설정
    actMinutes = getattr(settings, 'ACCESS_EXPIRE_TIME')
    actExpire_time = datetime.now() + timedelta(minutes=actMinutes),  # 엑세스 토큰 만료 시간 설정
    payload = {
        'user_id': user_id,
        'exp': actExpire_time,
        'type': access
    }

    # JWT 토큰 생성
    jwt_token = jwt.encode(payload, getattr(settings, 'SECRET_KEY'), algorithm)

    return jwt_token

def generateRefreshToken(user_id):
    # 리프레시 토큰 만료 기간 설정
    refDays = getattr(settings, 'REFRESH_EXPIRE_DAY')
    refExpire_time = datetime.now() + timedelta(days=refDays)  
    
    payload = {
        'user_id': user_id,
        'exp' : refExpire_time,
        'type': refresh
    }

    # JWT 토큰 생성
    jwt_token = jwt.encode(payload, getattr(settings, 'SECRET_KEY'), algorithm)

    return jwt_token 
   

def saveRefreshToken(user_id, refresh_token):
    cache_key = user_id
    cache_value = refresh_token
    expire_time = getattr(settings, "REFRESH_EXPIRE_TIME")
    
    cache.set(key=cache_key, value=cache_value, timeout=expire_time)      # redis에 저장
   
    