from django.shortcuts import render
from django.views.generic import TemplateView


class About(TemplateView):
    """CBV для страницы информации."""

    template_name = 'pages/about.html'


class Rules(TemplateView):
    """CBV для страницы правил."""

    template_name = 'pages/rules.html'


def csrf_failure(request, reason=''):
    """Кастомная страница ошибки 403-csrf."""
    return render(request, 'pages/403csrf.html', status=403)


def not_found(request, exception):
    """Кастомная страница ошибки 404."""
    return render(request, 'pages/404.html', status=404)


def internal_error(request):
    """Кастомная страница ошибки 500."""
    return render(request, 'pages/500.html', status=500)
