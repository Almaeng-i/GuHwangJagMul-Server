from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpRequest
from accounts.models import CustomUser
from GHJM.json_response_setting import  JsonResponse
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods
from todo.models import Todo
from almaengI.models import Character
from django.utils import timezone
from GHJM.utils import parse_json_body
from apscheduler.schedulers.background import BackgroundScheduler
import json


# Create your views here.
@require_http_methods(['POST'])
def create_todo(request):
    user = request.user
    todo_data, error_response = parse_json_body(request)

    if error_response:
        return error_response
    
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
    todo_data, error_response = parse_json_body(request)

    if error_response:
        return error_response
   
    id = todo_data.get('id')
    title = todo_data.get('title')
    
    if not id or not title:
        return JsonResponse({'error': 'id와 todo는 필수 입력 값 입니다.'}, status=400)

    try:
        # 해당 id와 user에 맞는 Todo 선택
        todo = Todo.objects.get(id=id)
    except Todo.DoesNotExist:
        return JsonResponse({'error': '해당 id에 대한 todo를 조회할 수 없습니다. id값이 올바른지 확인해 주세요.'}, status=404)

    todo.title = title
    
    try:
        todo.full_clean()   # 유효성 검사 -> Models
        todo.save()
        return JsonResponse({'sucess': 'todo를 수정이 완료되었습니다.'})
    except ValidationError as e:
        return JsonResponse({'error': e.message_dict}, status=400)
    

@require_http_methods(['PATCH'])
def is_success(request):    
    todo_data, error_response = parse_json_body(request)

    if error_response:
        return error_response
    
    id = todo_data.get('id')
    
    if id is None:
        return JsonResponse({'error': 'id는 필수 입력 값 입니다.'}, status=400)
    
    try:
        todo = Todo.objects.get(id=id)
    except Todo.DoesNotExist:
        return JsonResponse({'error': '해당 id에 대한 todo가 존재하지 않습니다. id값이 올바른지 확인해 주세요'}, status=404)
    
    todo.is_succeed = not todo.is_succeed
    
    try:
        todo.full_clean()  # 유효성 검사
        todo.save()
        return JsonResponse({'success': 'todo 완료 여부 수정 완료!'})
    except ValidationError as e:
        return JsonResponse({'error': e.message_dict}, status=400)


@require_http_methods(['DELETE'])
def delete_todo(request):
    todo_data, error_response = parse_json_body(request)

    if error_response:
        return error_response
    
    id = todo_data.get('id')
    
    if not id:
        return JsonResponse({'error': 'id는 필수 입력 값 입니다.'}, status=400)
    
    try:
        todo = Todo.objects.get(id=id)
    except Todo.DoesNotExist:
        return JsonResponse({'error': '해당 id에 대한 todo가 존재하지 않습니다.'}, status=404)
    
    todo.delete()
    
    return JsonResponse({'Success': 'todo가 정상적으로 삭제되었습니다.'})
    

@require_http_methods(['GET'])
def get_my_todo_list(request):
    todo_data, error_response = parse_json_body(request)

    if error_response:
        return error_response
    
    year = todo_data.get('year')
    month = todo_data.get('month')
    day = todo_data.get('day')
    
    if not year or not month or not day:
        return JsonResponse({'error': '년, 월, 일 은 필수 입력 값 입니다.'}, status=400)
    
    
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
    
    # safe False로 지정하여 리스트 값도 반환할 수 있도록 설정.
    return JsonResponse(todos_data, safe=False)

def update_character_exp(user, grant_exp):
    max_exp = 200
    characters = Character.objects.filter(user=user).exclude(exp=max_exp)
    
    for character in characters:
        character.exp += grant_exp
        character_exp = character.exp
        
        if character_exp <= 20:
            character.level = 1
        elif character_exp > 20 and character_exp <= 50:
            character.level = 2
        elif character_exp > 50 and character_exp <= 100:
            character.level = 3
        elif character_exp > 100 and character_exp <= max_exp:
            character.level = 4      
        elif character_exp > max_exp:
            character_exp = max_exp      
        
        character.save()


# 특정 사용자에 대해 지정된 날짜의 모든 Todo 항목의 is_succeed 값을 리스트 형태로 가져옴
def get_todo_success_list(user, year, month, day):
    success_list = list(Todo.objects.filter(
        user=user,
        created_at__year=year,
        created_at__month=month,
        created_at__day=day
    ).values_list('is_succeed', flat=True))
    return success_list


def todo_exp(user, year, month, day):
    # 특정 사용자의 지정된 날짜의 성공한 Todo 항목 개수를 세어 경험치를 업데이트.
    success_list = get_todo_success_list(user, year, month, day)
    grant_exp = sum(success_list)
    update_character_exp(user, grant_exp)   
    
    
def monthly_todo_exp(user, year, month):
    success_list = get_todo_success_list(user, year, month)
    success_cnt = sum(success_list)
    grant_exp = success_cnt * 5     # 한달 목표 달성했을 경우 5% 성장 포인트 부여.
    update_character_exp(user, grant_exp)  


def scheduled_job():
    users = CustomUser.objects.all()
    today = timezone.now().date()
    for user in users:
        todo_exp(user, today.year, today.month, today.day)

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_job, 'cron', hour=0, minute=0)  # 매일밤 자정에 실행되도록 설정
scheduler.start()
