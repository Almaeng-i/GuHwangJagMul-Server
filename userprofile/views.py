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
from django.core.exceptions import ValidationError


AWS_ACCESS_KEY = getattr(settings, 'AWS_ACCESS_KEY')
AWS_SECRET_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
AWS_BUCKET_ROOT_FOLDER_NAME = getattr(settings, 'AWS_BUCKET_ROOT_FOLDER_NAME')
DEFAULT_PROFILE_URL = getattr(settings, 'DEFAULT_PROFILE_URL')
RECEIVE_IMG_ENDPOINT = getattr(settings, 'RECEIVE_IMG_ENDPOINT')


def is_vaild_url(url):
    try:
        result = urlparse(url)
        # scheme과 netloc이 존재하는지 확인. (ex ->  http://example.com)
        if not all([result.scheme, result.netloc]):
            return False
            
        # 접근 가능성 확인
        with urlopen(url) as response:
            return response.status == 200
    except (ValueError, HTTPError, URLError):  # 분석할 구문이 존재하지 않을 경우 혹은 요청 실패
        return False

@require_http_methods(['POST'])
def create_user_profile(request):
    user = request.user           # user별로 식별 가능하기 위해 
    
    if UserProfile.objects.filter(user=user).exists():
        return JsonResponse({'error': '이미 존재하는 user 입니다.'}, status=409)
        
    user_profile_data = json.loads(request.body)
    
    user_nickname = user_profile_data.get('nickname') 
    intro = user_profile_data.get('user_introduction')
    img_url = user_profile_data.get('profile_picture_url')       # client에게 값을 가져옴
    
    if not is_vaild_url(img_url):
        return JsonResponse({'error': '잘못된 url 형식입니다.'}, status=400)
        
    user_profile = UserProfile(
        user=user, 
        nickname=user_nickname,
        profile_picture_url=img_url,
        user_introduction=intro
    )
    
    user_profile.save()
    
    return HttpResponse("Success!")
    
   
@require_http_methods(['PUT'])
def update_user_profile(request):
    user = request.user
    request_data = json.loads(request.body)
    
    id = request_data.get('id')
    
    if not id:
        return JsonResponse({'error': 'id는 필수 입력값 입니다.'}, status=400)
        
    user_nickname = request_data.get('nickname')
    intro = request_data.get('user_introduction')
    img_url = request_data.get('profile_picture_url')
    
    if len(user_nickname) > 10:
        return JsonResponse({'error': '닉네임은 10자 내외로 작성해 주세요.'}, status=400)
    
    if not is_vaild_url(img_url): 
        return JsonResponse({'error': '잘못된 url 형식입니다.'}, status=400)    
    
    try:    
        userprofile = UserProfile.objects.get(id=id)
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': '해당 id에 대한 user profile을 조회할 수 없습니다. id값이 올바른지 확인해 주세요.'}, status=404)
    
    userprofile.nickname = user_nickname
    userprofile.user_introduction = intro
    userprofile.profile_picture_url = img_url

    try:
        userprofile.full_clean()
        userprofile.save()
    except ValidationError as e:
        return JsonResponse({'error': e.error_dict}, status=400)

    return HttpResponse(status=204)    
        
    
    
@require_http_methods(["GET"])
def response_userprofile(request):
    user = request.user
    userprofile = UserProfile.objects.filter(user=user).first() # first 키워드를 사용해 1개의 userprofile 객체 반환.
    
    if userprofile == None:
        return JsonResponse({'error': f'{user}에 대한 userprofile을 찾을 수 없습니다.'}, status=404)
        
    id = userprofile.id
    user_nickname = userprofile.nickname
    intro = userprofile.user_introduction
    img_url = userprofile.profile_picture_url
    
    return JsonResponse({'nickname':user_nickname, 'id': id, 'intro': intro, 'img_url': img_url})
