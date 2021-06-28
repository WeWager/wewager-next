from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response


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

        query_str = request.query_params.get("q", "")
        vector = SearchVector(*fields)
        query = SearchQuery(query_str, search_type="phrase")
        queryset = (
            Model.objects.annotate(search=vector)
            .filter(search__icontains=query_str)
            .annotate(rank=SearchRank(vector, query))
            .order_by("-rank")
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
