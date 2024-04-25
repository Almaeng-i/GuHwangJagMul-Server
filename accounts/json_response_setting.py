from django.http import JsonResponse as DjangoJsonResponse

class JsonResponse(DjangoJsonResponse):
    def __init__(self, data, encoder=None, safe=True, json_dumps_params=None, **kwargs):
        if json_dumps_params is None:
            json_dumps_params = {'ensure_ascii': False}
        super().__init__(data, encoder=encoder, safe=safe, json_dumps_params=json_dumps_params, **kwargs)
