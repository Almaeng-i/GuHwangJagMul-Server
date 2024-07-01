from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpRequest
from GHJM.json_response_setting import  JsonResponse
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods
from monthly_goal.models import MonthList
from django.utils import timezone
from GHJM.utils import parse_json_body
import json


@require_http_methods(['POST'])
def create_month_list(request):
    user = request.user
    month_data, error_response = parse_json_body(request)
    
    if error_response:
        return error_response
    
    title = month_data.get('title')
    
    monthly_goal = MonthList(user=user, title=title)
    
    try:
        monthly_goal.full_clean()
        monthly_goal.save()
        return HttpResponse('success!')
    except ValidationError as e:
        return HttpResponse(f'error: {e.message_dict}', status=400)
    

@require_http_methods(['PUT'])
def update_month_list(request):
    month_data, error_response = parse_json_body(request)
    
    if error_response:
        return error_response
    
    id = month_data.get('id')
    title = month_data.get('title')
    
    if not id or not title:
        return JsonResponse({'error': 'id와 title 값은 필수 입력값입니다.'}, status=400)
    
    try:
        month_list = MonthList.objects.get(id=id)
    except MonthList.DoesNotExist:
        return JsonResponse({'error': '해당 id에 대한 한달 목표를 조회할 수 없습니다. id값이 올바른지 확인 해 주세요.'}, status = 404)
    
    month_list.title = title 
    
    try:
        month_list.full_clean()   # 유효성 검사 -> Models
        month_list.save()
        return JsonResponse({'sucess': '한달 목표 수정이 완료되었습니다.'})
    except ValidationError as e:
        return JsonResponse({'error': e.message_dict}, status=400)
    
    
@require_http_methods(['PATCH'])
def is_success(request):
    month_data, error_response = parse_json_body(request)
    
    if error_response:
        return error_response
    
    id = month_data.get('id')
    
    if id is None:
        return JsonResponse({'error': 'id는 필수 입력 값 입니다.'}, status=400)
    
    try:
        month_list = MonthList.objects.get(id=id)
    except MonthList.DoesNotExist:
        return JsonResponse({'error': '해당 id에 대한 한달 목표가 존재하지 않습니다. id값이 올바른지 확인해 주세요'}, status=404)
    
    month_list.is_succeed = not month_list.is_succeed
    
    try:
        month_list.full_clean()  # 유효성 검사
        month_list.save()
        return JsonResponse({'success': '한달 목표 완료 여부 수정 완료!'})
    except ValidationError as e:
        return JsonResponse({'error': e.message_dict}, status=400)
    

@require_http_methods(['DELETE'])
def delete_month_list(request):
    month_data, error_response = parse_json_body(request)
    
    if error_response:
        return error_response
    
    id = month_data.get('id')
    
    if id is None:
        return JsonResponse({'error': 'id는 필수 입력 값 입니다.'}, status=400)
    
    try:
        month_list = MonthList.objects.get(id=id)
    except MonthList.DoesNotExist:
        return JsonResponse({'error': '해당 id에 대한 한달 목표가 존재하지 않습니다. id값이 올바른지 확인해 주세요'}, status=404)
    
    month_list.delete()        
    
    return JsonResponse({'Success': '한달 목표가 정상적으로 삭제되었습니다.'})


@require_http_methods(['GET'])
def get_my_month_list(request):
    month_data, error_response = parse_json_body(request)
    
    if error_response:
        return error_response
    
    year = month_data.get('year')
    month = month_data.get('month')    
    
    if not year or not month:
        return JsonResponse({'error': '년도 혹은 월 은 필수 입력값 입니다.'}, status=400)
    
    month_list = MonthList.objects.filter(
        created_at__year = year,
        created_at__month = month,
    )
    
    month_list_data = [{
        'id': one_month_list.id,
        'title': one_month_list.title,
        'is_succeed': one_month_list.is_succeed
    } for one_month_list in month_list]
    
    return JsonResponse(month_list_data, safe=False)
