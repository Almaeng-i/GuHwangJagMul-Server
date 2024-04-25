from django.conf import settings
from datetime import datetime, timedelta
from django.core.cache import cache
import jwt


access = 'AccessToken'
refresh = 'RefreshToken'
algorithm = getattr(settings, 'ALGORITHM')

def generate_access_token(user_id):
    act_time = getattr(settings, 'ACCESS_EXPIRE_TIME')
    # 엑세스 토큰 만료 시간 설정 
    # 한국시간으로 적용하기 위해 UTC - 9시간 -> 한국시간
    actExpire_time = datetime.now() + timedelta(seconds=act_time) - timedelta(hours=9)
    
    payload = {
        'user_id': user_id,
        'exp': actExpire_time,
        'type': access
    }

    # JWT 토큰 생성
    jwt_token = jwt.encode(payload, getattr(settings, 'SECRET_KEY'), algorithm)

    return jwt_token

def generate_refresh_token(user_id):
    # 리프레시 토큰 만료 기간 설정
    reftime = getattr(settings, 'REFRESH_EXPIRE_TIME')
    ref_expire_time = datetime.now() + timedelta(seconds=reftime) - timedelta(hours=9)  
    payload = {
        'user_id': user_id,
        'exp' : ref_expire_time,
        'type': refresh
    }

    # JWT 토큰 생성
    jwt_token = jwt.encode(payload, getattr(settings, 'SECRET_KEY'), algorithm)

    return jwt_token 
   
   
def decode_token(token):
    payload = jwt.decode(token, getattr(settings, 'SECRET_KEY'), algorithm)
    return payload


def get_token_exp(token):
    payload = decode_token(token)
    expire_time = payload.get('exp')
    expire_time_dt = datetime.fromtimestamp(expire_time)
    return expire_time_dt


def get_token_exp_in_str_format(token):
    expire_time_dt = get_token_exp(token)
    expire_time_dt_str = expire_time_dt.strftime('%Y-%m-%d %H:%M:%S')
    return expire_time_dt_str    
        

def save_refresh_token(user_id, refresh_token):
    refresh_token_expire_time = get_token_exp(refresh_token)
    
    # 토큰 만료시간 - 현재 시간
    expire_time = refresh_token_expire_time- datetime.now()  
    
    # 초 단위로 변환
    total_seconds = expire_time.total_seconds()
    
    # redis에 저장
    cache.set(key=user_id, value=refresh_token, timeout=total_seconds)
    

