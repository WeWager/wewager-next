from rest_framework import views, viewsets, mixins


class ListCreateViewSet(
    viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin
):
    """
    A viewset that provides `create` and `list` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """

    pass


class CreateListRetrieveViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    A viewset that provides `retrieve`, `create`, and `list` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """

    pass


class CreateViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    """
    A viewset that provides only the `create` action.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """

    pass