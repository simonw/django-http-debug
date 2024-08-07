import base64
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import DebugEndpoint, RequestLog


@csrf_exempt
def debug_view(request, path):
    try:
        endpoint = DebugEndpoint.objects.get(path=path)
    except DebugEndpoint.DoesNotExist:
        return None  # Allow normal 404 handling to continue

    if endpoint.logging_enabled:
        log_entry = RequestLog(
            endpoint=endpoint,
            method=request.method,
            query_string=request.META.get("QUERY_STRING", ""),
            headers=dict(request.headers),
        )
        log_entry.set_body(request.body)
        log_entry.save()

    content = endpoint.content
    if endpoint.is_base64:
        content = base64.b64decode(content)

    response = HttpResponse(
        content=content,
        status=endpoint.status_code,
        content_type=endpoint.content_type,
    )
    for key, value in endpoint.headers.items():
        response[key] = value

    return response
