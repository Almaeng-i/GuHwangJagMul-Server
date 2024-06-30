from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from .models import BucketList
from GHJM.json_response_setting import JsonResponse
from django.core.exceptions import ValidationError
from GHJM.utils import parse_json_body
import json


@require_http_methods(['POST'])
def create_bucket_list(request):
    user = request.user
    bucket_list_data, error_response = parse_json_body(request)
    
    if error_response:
        return error_response
    
    title = bucket_list_data.get('title')
    content = bucket_list_data.get('content')
    
    bucket_list = BucketList(user=user, title=title, content=content)
    
    
    try:
        bucket_list.full_clean()
        bucket_list.save()
        return HttpResponse('Success!')
    
    except ValidationError as e:
            return HttpResponse(f'error: {e.message_dict}', status=400)
       

@require_http_methods(['PUT'])
def update_bucket_list(request):
    bucket_list_data, error_response = parse_json_body(request)
    
    if error_response:
        return error_response
    
    id = bucket_list_data.get('id')
    title = bucket_list_data.get('title')
    content = bucket_list_data.get('content')
    
    if id is None:
        return JsonResponse({'error': 'id는 필수 입력값 입니다.'})
    
    try:
        bucket_list = BucketList.objects.get(id=id)
    except BucketList.DoesNotExist:
        return JsonResponse({'error': '해당 id에 대한 bucket list 값이 존재하지 않습니다. id값이 올바른지 확인해 주세요'}, status=404)
    
    
    # db에 수정된 title, content 값 지정. -> 저장은 .save() 함수를 통해 변경사항 저장.
    bucket_list.title = title
    bucket_list.content = content
    
    try:
        bucket_list.full_clean()
        bucket_list.save()
        return JsonResponse({'Success': 'Bucket List 수정을 완료하였습니다.'})
    
    except ValidationError as e:
            return JsonResponse({'error': e.message_dict}, status=400)
    
    
@require_http_methods(['PATCH'])
def is_success(request):
    bucket_list_data, error_response = parse_json_body(request)
    
    if error_response:
        return error_response
    
    id = bucket_list_data.get('id')
    
    if id is None:
        return JsonResponse({'error': 'id는 필수 입력 값 입니다.'}, status=400)
        
    try:
        bucket_list = BucketList.objects.get(id=id)
    except BucketList.DoesNotExist:
        return JsonResponse({'error': '해당 id에 대한 bucekt list가 존재하지 않습니다. id값이 올바른지 확인해 주세요'}, status=404)
        
    bucket_list.is_succeed = not bucket_list.is_succeed
    
    try:
        bucket_list.full_clean()
        bucket_list.save()
        return JsonResponse({'success': 'bucket list 완료 여부 수정 완료!'})
    except ValidationError as e:
        return JsonResponse({'error': e.message_dict}, status=400)
    
    
@require_http_methods(['DELETE'])
def delete_bucket_list(request):
    bucket_list_data, error_response = parse_json_body(request)
    
    if error_response:
        return error_response
    
    id = bucket_list_data.get('id')
    
    if id is None:
        return JsonResponse({'error': 'id는 필수 입력 값 입니다.'}, status=400)
        
    try:
        bucket_list = BucketList.objects.get(id=id)
    except BucketList.DoesNotExist:
        return JsonResponse({'error': '해당 id에 대한 bucekt list가 존재하지 않습니다. id값이 올바른지 확인해 주세요'}, status=404)
    
    bucket_list.delete()
    
    return JsonResponse({'success': 'bucket list가 정상적으로 삭제되었습니다.'})


@require_http_methods(['GET'])
def get_my_bucket_list(request):
    bucket_list_data, error_response = parse_json_body(request)
    
    if error_response:
        return error_response
    
    year = bucket_list_data.get('year')
    
    try:
        year = int(year)
        
    except ValueError:
        return JsonResponse({'error': '년도 타입은 정수형만 입력가능합니다.'}, status=400)
    
    except ValidationError as e:
        return JsonResponse({'error': e.message_dict}, status=400)    
    
    
    bucket_list = BucketList.objects.filter(
        created_at__year=year
    )
    
    bucket_lists_data = [{
        'id': each_bucket_list.id,
        'title': each_bucket_list.title,
        'content': each_bucket_list.content,
        'is_success': each_bucket_list.is_succeed,
    } for each_bucket_list in bucket_list]
    
    return JsonResponse(bucket_lists_data, safe=False)
