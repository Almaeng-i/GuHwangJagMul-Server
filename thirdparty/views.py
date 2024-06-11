from django.http import JsonResponse
from GHJM import settings
from django.views import View
from accounts.models import CustomUser
from django.views.decorators.http import require_http_methods 
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import boto3, uuid
# Create your views here.
AWS_ACCESS_KEY = getattr(settings, 'AWS_ACCESS_KEY')
AWS_SECRET_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
AWS_BUCKET_ROOT_FOLDER_NAME = getattr(settings, 'AWS_BUCKET_ROOT_FOLDER_NAME')
DEFAULT_PROFILE_URL = getattr(settings, 'DEFAULT_PROFILE_URL')


@require_http_methods(['POST'])
def receive_img(request):
    img = request.FILES.get('profile_picture_url')
    
    img_url = DEFAULT_PROFILE_URL
    
    if img != None:
        try:
            uploader = ProfileUpload(img)
            img_url = uploader.upload() 
        except ClientError as e:
            return JsonResponse({"error": f"Server error: {e.response['Error']['Code']}"}, status=400)
        
    
    return JsonResponse({'img_url': img_url})


class ProfileUpload:
    
    def __init__(self, file):
        self.file = file
    
    def upload(self):       # 사용할 서비스, 액세스, 시크릿 키 순서
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
                "ContentType": self.file.content_type,
            }
        )   
        
        s3_img_url = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{key}'
        
        return s3_img_url

