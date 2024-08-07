from django.contrib import admin
from django.utils.html import format_html
from .models import DebugEndpoint, RequestLog


@admin.register(DebugEndpoint)
class DebugEndpointAdmin(admin.ModelAdmin):
    list_display = ("path", "status_code")
    search_fields = ("path",)


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ("endpoint", "method", "timestamp", "body_preview", "is_base64")
    list_filter = ("endpoint", "method", "is_base64")
    readonly_fields = (
        "endpoint",
        "method",
        "headers",
        "body_display",
        "is_base64",
        "timestamp",
    )
    search_fields = ("endpoint__path",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def body_preview(self, obj):
        body = obj.get_body()
        if isinstance(body, bytes):
            return f"Binary data ({len(body)} bytes)"
        return body[:50] + ("..." if len(body) > 50 else "")

    def body_display(self, obj):
        body = obj.get_body()
        if isinstance(body, bytes):
            return format_html("<pre>Binary data ({} bytes)</pre>", len(body))
        return format_html("<pre>{}</pre>", body)

    body_display.short_description = "Body"
