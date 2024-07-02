from .models import CustomUser
from django.http import JsonResponse
from django.conf import settings
from jwt.exceptions import InvalidSignatureError, ExpiredSignatureError
from GHJM.json_response_setting import JsonResponse
import datetime
import jwt

algorithm = getattr(settings, 'ALGORITHM')
secret_key = getattr(settings, 'SECRET_KEY')

class AccessTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # true면 실행
        if self.check_path_to_exclude_middleware(request.path): 
            response = self.get_response(request)
            return response
        
        
        # 클라이언트의 요청에서 헤더에서 AccessToken을 추출.
        authorization_header = request.headers.get('AUTHORIZATION')
        
        try:
            token = authorization_header  # 인가코드
            
            if token is None:
                raise ValueError("토큰이 없습니다.")
                
            
            # AccessToken을 복호화하여 사용자를 인증
            payload = jwt.decode(token, secret_key, algorithms=algorithm)
            
            # payload에서 사용자 식별 정보를 추출
            id = payload.get('user_id')

            # 추출된 사용자 식별 정보를 사용하여 사용자를 가져옴.
            try:
                user = CustomUser.objects.get(id=id)
            except CustomUser.DoesNotExist:
                return JsonResponse({'error': '해당 id에 대한 user 객체가 존재하지 않습니다.'}, status=404)
            
            # 인증이 성공하면 요청에 사용자를 할당.
            request.user = user
        
        except ValueError as e:
            error_message = str(e)
            return JsonResponse({'error': error_message}) 
        
        except InvalidSignatureError:
            return JsonResponse({'error' : '유효하지 않은 토큰 값 입니다.'})
        
        except ExpiredSignatureError:
            return JsonResponse({'error' : '만료된 토큰 값 입니다.'})

        return  self.get_response(request)   # views를 거친후에 처리됨.
    
    # 미들웨어를 제외할 경로 탐색 -> Oauth, admin, refresh page
    def check_path_to_exclude_middleware(self, path):
        except_path = ['kakao', 'refresh', 'admin', 'logout']
        for each_path in except_path:
            if each_path in path:
                return True
        return False
