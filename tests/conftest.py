from django.conf import settings

urlpatterns = []


def pytest_configure():
    settings.configure(
        SECRET_KEY="django-insecure-test-key",
        DEBUG=True,
        ALLOWED_HOSTS=["*"],
        INSTALLED_APPS=[
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            # "django.contrib.sessions",
            # "django.contrib.messages",
            # "django.contrib.staticfiles",
            "django_http_debug",
        ],
        MIDDLEWARE=[
            "django_http_debug.middleware.DebugMiddleware",
        ],
        ROOT_URLCONF=__name__,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        USE_TZ=True,
    )
