from django.db import models
import base64


class DebugEndpoint(models.Model):
    path = models.CharField(max_length=255, unique=True)
    status_code = models.IntegerField(default=200)
    headers = models.JSONField(default=dict, blank=True)
    content = models.TextField(blank=True)

    def __str__(self):
        return self.path


class RequestLog(models.Model):
    endpoint = models.ForeignKey(DebugEndpoint, on_delete=models.CASCADE)
    method = models.CharField(max_length=10)
    headers = models.JSONField()
    body = models.TextField(blank=True)
    is_base64 = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method} {self.endpoint.path} at {self.timestamp}"

    def set_body(self, body):
        try:
            # Try to decode as UTF-8
            self.body = body.decode("utf-8")
            self.is_base64 = False
        except UnicodeDecodeError:
            # If that fails, store as base64
            self.body = base64.b64encode(body).decode("ascii")
            self.is_base64 = True

    def get_body(self):
        if self.is_base64:
            return base64.b64decode(self.body.encode("ascii"))
        return self.body
