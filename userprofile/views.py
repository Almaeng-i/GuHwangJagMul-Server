from django.shortcuts import get_object_or_404
from userprofile.models import UserProfile
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from GHJM import settings
from accounts.models import CustomUser
import boto3, uuid

AWS_ACCESS_KEY = getattr(settings, 'AWS_ACCESS_KEY')
AWS_SECRET_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
AWS_BUCKET_ROOT_FOLDER_NAME = getattr(settings, 'AWS_BUCKET_ROOT_FOLDER_NAME')


class ProfileUpload:
    def __init__(self, file):
        self.file = file
    
    def upload(self):       # 사용할 서비스, 액세스, 시크릿 키 순서
        if self.file == None:
            return JsonResponse({'Failed': '프로필 사진이 업로드 되지 않았습니다.'})
        
        s3_client = boto3.client(
            's3',       
            aws_access_key_id = AWS_ACCESS_KEY,
            aws_secret_access_key = AWS_SECRET_KEY
        )
        key = f'{AWS_BUCKET_ROOT_FOLDER_NAME}/{uuid.uuid1().hex}'
    
        s3_client.upload_fileobj(
            self.file,
            AWS_STORAGE_BUCKET_NAME,
            key,
            ExtraArgs={
                "ContentType": self.file.content_type
            }
        )   
        
        s3_img_url = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{key}'
        
        return s3_img_url



@require_http_methods(['POST'])
def save_user_profile(request):
    user = request.user           # user별로 식별 가능하기 위해 
    picture = request.FILES.get('profile_picture_url')      # img 파일을 받기 위해 FILES 사용
    intro = request.POST.get('user_introduction')        # 한줄 소개 
    
    uploader = ProfileUpload(picture)   
    s3_img_url = uploader.upload()
    
    user_profile = UserProfile(user=user, profile_picture_url=s3_img_url, user_introduction=intro)
    user_profile.save()
    
    profile_id = user_profile.id
    
    return JsonResponse({'success': True, 'profile_id': profile_id,'image_url': s3_img_url})
