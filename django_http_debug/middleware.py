from .views import debug_view


class DebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404:
            path = request.path.lstrip("/")
            debug_response = debug_view(request, path)
            if debug_response:
                return debug_response
        return response
