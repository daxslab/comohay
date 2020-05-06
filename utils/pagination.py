from rest_framework.pagination import PageNumberPagination


class BasicSizePaginator(PageNumberPagination):
    page_size_query_param = 'size'