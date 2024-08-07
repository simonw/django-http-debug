from django_http_debug import example_function


def test_example_function():
    assert example_function() == 2
