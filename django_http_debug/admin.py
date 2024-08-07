import re
import filetype
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import DebugEndpoint, RequestLog

sequence_re = re.compile(r"((?:\\x[0-9a-f]{2})+)")
octet_re = re.compile(r"(\\x[0-9a-f]{2})")

QUERY_STRING_TRUNCATE = 16


@admin.register(DebugEndpoint)
class DebugEndpointAdmin(admin.ModelAdmin):
    list_display = ("path", "status_code", "logging_enabled")
    list_filter = ("logging_enabled",)


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "endpoint",
        "method",
        "query_string_truncated",
        "body_preview",
        "is_base64",
    )
    list_filter = ("endpoint", "method", "is_base64")
    readonly_fields = (
        "endpoint",
        "query_string",
        "method",
        "headers",
        "body",
        "body_display",
        "is_base64",
        "timestamp",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def query_string_truncated(self, obj):
        return obj.query_string[:QUERY_STRING_TRUNCATE] + (
            "…" if len(obj.query_string) > QUERY_STRING_TRUNCATE else ""
        )

    query_string_truncated.short_description = "Query string"

    def body_preview(self, obj):
        body = obj.get_body()
        if isinstance(body, bytes):
            return f"Binary data ({len(body)} bytes)"
        return body[:50] + ("..." if len(body) > 50 else "")

    body_preview.short_description = "Body preview"

    def body_display(self, obj):
        body = obj.get_body()
        if not isinstance(body, bytes):
            return format_html("<pre>{}</pre>", body)

        # Attempt to guess filetype
        suggestion = None
        match = filetype.guess(body[:1000])
        if match:
            suggestion = "{} ({})".format(match.extension, match.mime)

        encoded = repr(body)
        # Ditch the b' and trailing '
        if encoded.startswith("b'") and encoded.endswith("'"):
            encoded = encoded[2:-1]

        # Split it into sequences of octets and characters
        chunks = sequence_re.split(encoded)
        html = []
        if suggestion:
            html.append(
                '<p style="margin-top: 0; font-family: monospace; font-size: 0.8em;">Suggestion: {}</p>'.format(
                    suggestion
                )
            )
        for chunk in chunks:
            if sequence_re.match(chunk):
                octets = octet_re.findall(chunk)
                octets = [o[2:] for o in octets]
                html.append(
                    '<code style="color: #999; font-family: monospace">{}</code>'.format(
                        " ".join(octets).upper()
                    )
                )
            else:
                html.append(chunk.replace("\\\\", "\\"))

        return mark_safe(" ".join(html).strip().replace("\\r\\n", "<br>"))
