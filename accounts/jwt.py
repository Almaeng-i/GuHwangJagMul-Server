from django.conf import settings
from .models import CustomUser
from datetime import datetime, timedelta
import jwt

Access = 'AccessToken'
Refresh = 'RefreshToken'

def generateAccessToken(user):
    # JWT payload로 claim 설정
    payload = {
        'user_id': user.id(),
        'exp': datetime.now() + timedelta(days=1),  # 토큰 만료 시간 설정
        'type': Access
    }

    # JWT 토큰 생성
    jwt_token = jwt.encode(payload, getattr(settings, 'KAKAO_REST_API_KEY'), algorithm='HS256')

    return jwt_token

def generateRefreshToken(user):
    payload = {
        'user_id': user.id(),
        'exp': datetime.now() + timedelta(days=1),  # 토큰 만료 시간 설정
        'type': Refresh
    }

    # JWT 토큰 생성
    jwt_token = jwt.encode(payload, getattr(settings, 'KAKAO_REST_API_KEY'), algorithm='HS256')

    return jwt_token    
