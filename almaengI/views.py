from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from .models import Character
from GHJM.json_response_setting import  JsonResponse
import json

# Create your views here.

allowed_almaengi_type_list = ['고구마', '감자', '옥수수', '밤', '복숭아', '아보카도']

def is_almaengi_type_valid(almaengi_type):
   return almaengi_type in allowed_almaengi_type_list
        

@require_http_methods(["POST"])
def save_almaengi(request):
    print(request)
    user_id = request.user
    almaengi_data = json.loads(request.body)
    almaengi_type = almaengi_data.get('almaengi_type')
    almaengi_name = almaengi_data.get('almaengi_name')
    
    if not is_almaengi_type_valid(almaengi_type):
        return JsonResponse({'error': '잘못된 알맹이 타입입니다!'}) 
    
    character = Character(user=user_id, character_type=almaengi_type, name=almaengi_name)
    character.save()
    
    return HttpResponse("Success!")

