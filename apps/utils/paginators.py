from rest_framework.pagination import PageNumberPagination


class BaseResultsPagination(PageNumberPagination):
    """ Base paginator for any objects result. """
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100
