from django.shortcuts import get_object_or_404
from userprofile.models import UserProfile
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from GHJM import settings
from GHJM.json_response_setting import JsonResponse
from thirdparty.views import receive_img, ProfileUpload
from urllib.parse import urlparse
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import boto3, uuid, requests, json

AWS_ACCESS_KEY = getattr(settings, 'AWS_ACCESS_KEY')
AWS_SECRET_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
AWS_BUCKET_ROOT_FOLDER_NAME = getattr(settings, 'AWS_BUCKET_ROOT_FOLDER_NAME')
DEFAULT_PROFILE_URL = getattr(settings, 'DEFAULT_PROFILE_URL')
RECEIVE_IMG_ENDPOINT = getattr(settings, 'RECEIVE_IMG_ENDPOINT')


def is_vaild_url(url):
    parse_url = urlparse(url)
    try:
        result = urlparse(url)
        # scheme과 netloc이 존재하는지 확인. (ex ->  http://example.com)
        if all([result.scheme, result.netloc]):
            try:
                # 접근 가능성 확인
                with urlopen(url) as response:
                    return response.status == 200
            except (HTTPError, URLError):
                return False
        
        return False
    
    except BaseException:       # 파이썬 최상위 Exception -> 모든 Error Catch
        return False

@require_http_methods(['POST'])
def create_user_profile(request):
    user = request.user           # user별로 식별 가능하기 위해 
    
    if UserProfile.objects.filter(user=user).exists():
        return JsonResponse({'error': '이미 존재하는 user 입니다.'}, status=409)
        
    request_data = json.loads(request.body)
    
    intro = request_data.get('user_introduction')
    img_url = request_data.get('profile_picture_url')       # client에게 값을 가져옴
    
    
    if is_vaild_url(img_url):
        user_profile = UserProfile(user=user, profile_picture_url=img_url, user_introduction=intro)
        user_profile.save()
        return HttpResponse("Success!")
    
    else:
        return JsonResponse({'error': '잘못된 url 형식입니다.'}, status=400)
        
    
   
@require_http_methods(['PUT'])
def update_user_profile(request):
    user = request.user
    request_data = json.loads(request.body)
    
    id = request_data.get('id')
    intro = request_data.get('user_introduction')
    img_url = request_data.get('profile_picture_url')
    
    if is_vaild_url(img_url): 
        UserProfile.objects.filter(id=id).update(user_introduction = intro, profile_picture_url = img_url)
        return HttpResponse(status=204)    
    
    else:
        return JsonResponse({'error': '잘못된 url 형식입니다.'}, status=400)       
        
    
    
@require_http_methods(["GET"])
def response_userprofile(request):
    user = request.user
    userprofile = UserProfile.objects.filter(user=user).first() # first 키워드를 사용해 1개의 userprofile 객체 반환.
    
    
    try:
        if userprofile != None:
            id = userprofile.id
            intro = userprofile.user_introduction
            img_url = userprofile.profile_picture_url
            
            return JsonResponse({'id': id, 'intro': intro, 'img_url': img_url})
        
        else:
            raise AttributeError
        
    except AttributeError:
        return JsonResponse({'error': f'{user}에 대한 userprofile을 찾을 수 없습니다.'}, status=404)
    
    
