import pytest
from django_http_debug.models import DebugEndpoint, RequestLog


@pytest.mark.django_db
def test_debug_view(client):
    assert client.get("/test/endpoint").status_code == 404
    DebugEndpoint.objects.create(
        path="test/endpoint",
        status_code=200,
        content="Test content",
        content_type="text/plain",
    )
    response = client.get("/test/endpoint")
    assert response.status_code == 200
    assert response.content == b"Test content"
    assert response["Content-Type"] == "text/plain"


@pytest.mark.django_db
def test_request_logging(client):
    endpoint = DebugEndpoint.objects.create(
        path="test/log",
        status_code=200,
        content="Log test",
    )
    assert endpoint.requestlog_set.count() == 0

    client.get("/test/log?param=value")

    log = RequestLog.objects.filter(endpoint=endpoint).first()
    assert log is not None
    assert log.method == "GET"
    assert log.query_string == "param=value"


@pytest.mark.django_db
def test_logging_disabled(client):
    DebugEndpoint.objects.create(
        path="test/nolog",
        status_code=200,
        content="No log test",
        logging_enabled=False,
    )

    assert client.get("/test/nolog").status_code == 200

    assert RequestLog.objects.count() == 0


@pytest.mark.django_db
def test_base64_content(client):
    import base64

    content = base64.b64encode(b"Binary content").decode()
    DebugEndpoint.objects.create(
        path="test/binary",
        status_code=200,
        content=content,
        is_base64=True,
        content_type="application/octet-stream",
    )

    response = client.get("/test/binary")
    assert response.status_code == 200
    assert response.content == b"Binary content"
    assert response["Content-Type"] == "application/octet-stream"


@pytest.mark.django_db
def test_custom_headers(client):
    DebugEndpoint.objects.create(
        path="test/headers",
        status_code=200,
        content="Custom headers test",
        headers={"X-Custom-Header": "Test Value"},
    )

    response = client.get("/test/headers")
    assert response.status_code == 200
    assert response["X-Custom-Header"] == "Test Value"
