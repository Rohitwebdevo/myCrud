import json
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from .models import Item


def _bad_request(msg='Bad request'):
    return JsonResponse({'error': msg}, status=400)


@csrf_exempt
def items_list(request):
    if request.method == 'GET':
        items = Item.objects.all().order_by('-created_at')
        data = [i.to_dict() for i in items]
        return JsonResponse(data, safe=False)

    if request.method == 'POST':
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except Exception:
            return _bad_request('Invalid JSON')

        name = payload.get('name')
        description = payload.get('description', '')
        if not name:
            return _bad_request('`name` is required')

        item = Item.objects.create(name=name, description=description)
        return JsonResponse(item.to_dict(), status=201)

    return HttpResponseNotAllowed(['GET', 'POST'])


@csrf_exempt
def item_detail(request, pk):
    try:
        item = Item.objects.get(pk=pk)
    except Item.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse(item.to_dict())

    if request.method in ('PUT', 'PATCH'):
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except Exception:
            return _bad_request('Invalid JSON')

        name = payload.get('name')
        description = payload.get('description')
        if name is not None:
            item.name = name
        if description is not None:
            item.description = description
        item.save()
        return JsonResponse(item.to_dict())

    if request.method == 'DELETE':
        item.delete()
        return JsonResponse({'deleted': True})

    return HttpResponseNotAllowed(['GET', 'PUT', 'PATCH', 'DELETE'])
