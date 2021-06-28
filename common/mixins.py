from django.contrib.postgres.search import SearchVector
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response


class ReadWriteSerializerMixin(object):
    """
    Overrides get_serializer_class to choose the read serializer
    for GET requests and the write serializer for POST requests.

    Set read_serializer_class and write_serializer_class attributes on a
    viewset.
    """

    read_serializer_class = None
    write_serializer_class = None

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return self.get_write_serializer_class()
        return self.get_read_serializer_class()

    def get_read_serializer_class(self):
        assert self.read_serializer_class is not None, (
            "'%s' should either include a `read_serializer_class` attribute,"
            "or override the `get_read_serializer_class()` method."
            % self.__class__.__name__
        )
        return self.read_serializer_class

    def get_write_serializer_class(self):
        assert self.write_serializer_class is not None, (
            "'%s' should either include a `write_serializer_class` attribute,"
            "or override the `get_write_serializer_class()` method."
            % self.__class__.__name__
        )
        return self.write_serializer_class


class SearchActionMixin:
    """
    Adds a /search?q=<query> action to a `ViewSet`.
    
    This action assumes your ViewSet has a `queryset` and `serializer_class`.
    
    Also requires you to set `search_fields`, a list containing model fields to
    search against.
    """

    search_fields = []

    @action(methods=["GET"], detail=False)
    def search(self, request: Request):
        if hasattr(self, "queryset") and self.queryset is not None:
            Model = self.queryset.model
        elif hasattr(self, "get_queryset"):
            Model = self.get_queryset().model

        assert Model is not None, "SearchActionMixin requires a model"
        
        fields = getattr(self, "search_fields")
        if fields == []:
            fields = Model._meta.fields

        queryset = Model.objects.annotate(
            search=SearchVector(*fields)
        ).filter(search=request.query_params.get("q", ""))
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)