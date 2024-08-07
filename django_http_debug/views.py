from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import DebugEndpoint, RequestLog


@csrf_exempt
def debug_view(request, path):
    try:
        endpoint = DebugEndpoint.objects.get(path=path)
    except DebugEndpoint.DoesNotExist:
        return None  # Allow normal 404 handling to continue

    # Log the request
    log_entry = RequestLog(
        endpoint=endpoint,
        method=request.method,
        headers=dict(request.headers),
    )
    log_entry.set_body(request.body)
    log_entry.save()

    # Prepare the response
    response = HttpResponse(
        content=endpoint.content, status=endpoint.status_code, content_type="text/plain"
    )
    for key, value in endpoint.headers.items():
        response[key] = value

    return response
