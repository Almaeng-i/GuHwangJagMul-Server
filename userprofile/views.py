from django.shortcuts import get_object_or_404
from userprofile.models import UserProfile
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from GHJM import settings
from GHJM.json_response_setting import JsonResponse
from thirdparty.views import receive_img
import boto3, uuid, requests, json

AWS_ACCESS_KEY = getattr(settings, 'AWS_ACCESS_KEY')
AWS_SECRET_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
AWS_BUCKET_ROOT_FOLDER_NAME = getattr(settings, 'AWS_BUCKET_ROOT_FOLDER_NAME')
DEFAULT_PROFILE_URL = getattr(settings, 'DEFAULT_PROFILE_URL')
RECEIVE_IMG_ENDPOINT = getattr(settings, 'RECEIVE_IMG_ENDPOINT')


@require_http_methods(['POST'])
def create_user_profile(request):
    user = request.user           # user별로 식별 가능하기 위해 
    request_data = json.loads(request.body)
    
    intro = request_data.get('user_introduction')
    img_url = request_data.get('profile_picture_url')
    
    user_profile = UserProfile(user=user, profile_picture_url=img_url, user_introduction=intro)
    user_profile.save()
    
    return HttpResponse("Success!")


@require_http_methods(['PUT'])
def update_user_profile(request):
    user = request.user
    request_data = json.loads(request.body)
    
    id = request_data.get('id')
    intro = request_data.get('user_introduction')
    img_url = request_data.get('profile_picture_url')
    
    UserProfile.objects.filter(id=id).update(user_introduction = intro, profile_picture_url = img_url)
    
    return HttpResponse(status=204)
    
    
    
@require_http_methods(["GET"])
def response_userprofile(request):
    user = request.user
    userprofile = UserProfile.objects.filter(user=user).first() # first 키워드를 사용해 1개의 userprofile 객체 반환.
    id = userprofile.id
    intro = userprofile.user_introduction
    img_url = userprofile.profile_picture_url
    
    return JsonResponse({'id': id, 'intro': intro, 'img_url': img_url})
    
    
