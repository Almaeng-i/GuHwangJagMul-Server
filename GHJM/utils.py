# utils.py
import json
from django.http import JsonResponse

def parse_json_body(request):
    try:
        return json.loads(request.body), None
    except json.JSONDecodeError:
        return None, JsonResponse(
            {'error': '유효하지 않은 JSON 값 입니다.'}, 
            status=400, 
            json_dumps_params={'ensure_ascii': False}
        )
