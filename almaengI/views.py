from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import Character
from GHJM.json_response_setting import  JsonResponse
import json

# Create your views here.

allowed_almaengi_type_list = ['고구마', '감자', '옥수수', '밤', '복숭아', '아보카도']

def validate_almaengi_type(almaengi_type):
    cnt = 0
    for allowed_almaengi_type in allowed_almaengi_type_list:
        if allowed_almaengi_type == almaengi_type:
           cnt += 1
    
    if cnt == 0: 
        return True
        

def save_almaengi(request):
    user_id = request.user
    almaengi_data = json.loads(request.body)
    almaengi_type = almaengi_data.get('almaengi_type')
    almaengi_name = almaengi_data.get('almaengi_name')
    
    if validate_almaengi_type(almaengi_type):
        return JsonResponse({'error': '잘못된 알맹이 타입입니다!'}) 
    
    character = Character(user=user_id, character_type=almaengi_type, name=almaengi_name)
    character.save()
    
    return HttpResponse("Success!")

