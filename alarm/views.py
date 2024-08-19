from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.conf import settings
from django.views import View
from accounts.models import CustomUser
from apns2.payload import Payload
from apns2.client import APNsClient
from apns2.credentials import CertificateCredentials
from django.core.exceptions import ObjectDoesNotExist
import json, logging


APNS_CERTIFICATE_PATH = getattr(settings, 'APNS_CERTIFICATE_PATH')
APNS_TOPIC = getattr(settings, 'APPLE_BUNDLE_ID')
CUSTOM_USER = get_user_model()
APPLE_TEAM_ID = getattr(settings, 'APPLE_TEAM_ID')
APPLE_BUNDLE_ID = getattr(settings, 'APPLE_BUNDLE_ID')
APPLE_AUTH_KEY_ID = getattr(settings, 'APPLE_AUTH_KEY_ID')

# 로깅 설정 (로거 생성)
logger = logging.getLogger(__name__)

def send_push_notification(user, message):
    try:
        device_token = user.device_token
        
        credentials = CertificateCredentials(APNS_CERTIFICATE_PATH)
        apns_client = APNsClient(credentials=credentials)
        
        payload = Payload(alert=message, sound='default', badge=1)
        apns_client.send_notification(device_token, payload, topic=APNS_TOPIC)
    except Exception as e:
        logger.error(f'알림 전송에 실패하였습니다. uid -> {user.id}: {e}')
