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
    user = request.user
    almaengi_data = json.loads(request.body)
    almaengi_type = almaengi_data.get('almaengi_type')
    almaengi_name = almaengi_data.get('almaengi_name')
    
    if not is_almaengi_type_valid(almaengi_type):
        return JsonResponse({'error': '잘못된 알맹이 타입입니다!'}, status=400) 
    
    character = Character(user=user, character_type=almaengi_type, name=almaengi_name)
    character.save()
    
    return HttpResponse("Success!")


@require_http_methods(["GET"])
def response_almaengi_info(request):
    user = request.user
    
    try:
        characters = Character.objects.filter(user=user)
        if not characters.exists():
            return JsonResponse({'error': '알맹이가 존재하지 않습니다.'}, status=404)
        
        characters_list = list(characters.values('id', 'character_type', 'name', 'level'))
    
        return JsonResponse(characters_list, safe=False)
    
    except Character.DoesNotExist:
            return JsonResponse({'error': '알맹이를 조회할 수 없습니다.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    