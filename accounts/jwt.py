from django.conf import settings
from datetime import datetime, timedelta
from django.core.cache import cache
import jwt

access = 'AccessToken'
refresh = 'RefreshToken'
algorithm = getattr(settings, 'ALGORITHM')

def generateAccessToken(user_id):
    act_time = getattr(settings, 'ACCESS_EXPIRE_TIME')
    actExpire_time = datetime.now() + timedelta(seconds=act_time)  # 엑세스 토큰 만료 시간 설정
    print(actExpire_time)
    
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
    reftime = getattr(settings, 'REFRESH_EXPIRE_TIME')
    refExpire_time = datetime.now() + timedelta(seconds=reftime)      
    payload = {
        'user_id': user_id,
        'exp' : refExpire_time,
        'type': refresh
    }

    # JWT 토큰 생성
    jwt_token = jwt.encode(payload, getattr(settings, 'SECRET_KEY'), algorithm)

    return jwt_token 
   
   
def decodeToken(token):
    try:
        payload = jwt.decode(token, getattr(settings, 'SECRET_KEY'), algorithm)
        return payload

    # 토큰 만료시 
    except jwt.ExpiredSignatureError:
        return None
    
    # 유효하지 않은 토큰일 경우
    except jwt.InvalidTokenError:
        return None
    
def getTokenExp(token):
    payload = decodeToken(token)
    expire_time = payload.get('exp')
    expire_time_dt = datetime.fromtimestamp(expire_time)
    return expire_time_dt

def getformatStrTokenExp(token):
    expire_time_dt = getTokenExp(token)
    expire_time_dt_str = expire_time_dt.strftime('%Y-%m-%d %H:%M:%S')
    return expire_time_dt_str
    

def saveRefreshToken(user_id, refresh_token):
    refresh_token_expire_time = getTokenExp(refresh_token)
    
    # 토큰 만료시간 - 현재 시간
    expire_time = refresh_token_expire_time- datetime.now()  
    
    # 초 단위로 변환
    total_seconds = expire_time.days * 86400 + expire_time.seconds + expire_time.microseconds / 1000000
    
    # redis에 저장
    cache.set(key=user_id, value=refresh_token, timeout=total_seconds)
    

