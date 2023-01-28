from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Page, Paginator
from django.db.models.query import QuerySet

NUMBERS_PAGES = 10


def get_page(queryset: QuerySet, request: WSGIRequest) -> Page:
    """Функция для разбиения записей из базы данных
    постранично.
    """
    paginator: Paginator = Paginator(queryset, NUMBERS_PAGES)
    page_number: str = request.GET.get('page')
    page_obj: Page = paginator.get_page(page_number)
    return {
        'page_obj': page_obj,
    }
