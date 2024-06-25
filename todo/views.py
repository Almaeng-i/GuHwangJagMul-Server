from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpRequest
from GHJM.json_response_setting import  JsonResponse
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods
from todo.models import Todo
from django.utils import timezone
import json

# Create your views here.
@require_http_methods(['POST'])
def create_todo(request):
    user = request.user
    todo_data = json.loads(request.body)
    
    title = todo_data.get('title')
    
    todo = Todo(user=user, title=title)
    
    try:
        todo.full_clean()     # 유효성 검사
        todo.save()
        return HttpResponse('Success!')
    except ValidationError as e:
        return HttpResponse(f'error: {e.message_dict}', status=400)
       

@require_http_methods(['PUT'])
def update_todo(request):
    todo_data = json.loads(request.body)
    id = todo_data.get('id')
    title = todo_data.get('title')
    
    if not id or not title:
        return JsonResponse({'error': '해당 user에 대한 todo가 존재하지 않습니다.'}, status=400)

    try:
        # 해당 id와 user에 맞는 Todo 선택
        todo = Todo.objects.get(id=id)
    except Todo.DoesNotExist:
        return JsonResponse({'error': 'todo를 조회할 수 없습니다.'})

    todo.title = title
    
    try:
        todo.full_clean()   # 유효성 검사 -> Models
        todo.save()
        return JsonResponse({'sucess': 'todo를 수정이 완료되었습니다.'})
    except ValidationError as e:
        return JsonResponse({'error': e.message_dict}, status=400)
    

@require_http_methods(['PATCH'])
def is_success(request):    
    try:
        todo_data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': '유효하지 않은 JSON 값 입니다.'}, status=400)
    
    id = todo_data.get('id')
    
    if id is None:
        return JsonResponse({'error': 'id는 필수 입력값 입니다.'}, status=400)
    
    try:
        todo = Todo.objects.get(id=id)
    except Todo.DoesNotExist:
        return JsonResponse({'error': 'todo가 존재하지 않습니다.'}, status=404)
    
    todo.is_succeed = not todo.is_succeed
    
    try:
        todo.full_clean()  # 유효성 검사
        todo.save()
        return JsonResponse({'success': 'todo 완료 여부 수정 완료!'})
    except ValidationError as e:
        return JsonResponse({'error': e.message_dict}, status=400)


@require_http_methods(['DELETE'])
def delete_todo(request):
    try:
        todo_data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': '유효하지 않은 JSON 값 입니다.'}, status=400)
    
    id = todo_data.get('id')
    
    if not id:
        return JsonResponse({'error': 'id는 필수 입력값 입니다.'}, status=400)
    
    try:
        todo = Todo.objects.get(id=id)
    except Todo.DoesNotExist:
        return JsonResponse({'error': 'todo가 존재하지 않습니다.'}, status=404)
    
    todo.delete()
    
    return JsonResponse({'Success': 'todo가 정상적으로 삭제되었습니다.'})
    

@require_http_methods(['GET'])
def get_my_todo_list(request):
    try:
        todo_data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': '유효하지 않은 JSON 값 입니다.'}, status=400)
    
    year = todo_data.get('year')
    month = todo_data.get('month')
    day = todo_data.get('day')
    
    if not year or not month or not day:
        return JsonResponse({'error': '년, 월, 일 은 필수 입력값 입니다.'}, status=400)
    
    
    todo_list = Todo.objects.filter(
        created_at__year=year,
        created_at__month=month,
        created_at__day=day
    )
    
    # todo list에서 하나의 todo 객체를 꺼내 해당 필드값을 리스트 형으로 저장
    todos_data = [{
        'id': todo.id,
        'title': todo.title,
        'is_succeed': todo.is_succeed,
        'created_at': todo.created_at.strftime("%Y-%m-%d %H:%M:%S")
    } for todo in todo_list]
    
    # safe False로 지정하여 딕셔너리 값도 반환할 수 있도록 설정.
    return JsonResponse(todos_data, safe=False)
