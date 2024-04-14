"""URL configuration for `api_rest` app."""

from collections.abc import Sequence

__all__: Sequence[str] = ("urlpatterns", "create_router", "app_name")

from collections.abc import Iterable, MutableSequence
from typing import Final, TypeVar

import django
from django.db.models import Model
from django.urls import URLPattern, URLResolver
from rest_framework.routers import BaseRouter, DefaultRouter

from api_rest.views import (
    BasePrefixableGenericViewSet,
    BasePrefixableViewSet,
    CourseViewSet,
    CustomAPIRootView,
    ModuleViewSet,
    MyUserDetailsView,
    OtherTagViewSet,
    PostViewSet,
    ReportViewSet,
    ToolTagViewSet,
    TopicTagViewSet,
    UniversityViewSet,
    UserViewSet,
)

model_T = TypeVar("model_T", bound=Model)  # noqa: N816

app_name: Final[str] = "api_rest"


def create_router() -> BaseRouter:
    class CustomRouter(DefaultRouter):
        root_view_name = "root"
        APIRootView = CustomAPIRootView

    router: BaseRouter = CustomRouter()

    VIEWSETS: Final[Iterable[type[BasePrefixableGenericViewSet[Model] | BasePrefixableViewSet]]] = (  # type: ignore[assignment] # noqa: E501
        UserViewSet,
        UniversityViewSet,
        CourseViewSet,
        ModuleViewSet,
        ToolTagViewSet,
        TopicTagViewSet,
        OtherTagViewSet,
        PostViewSet,
        ReportViewSet,
    )
    viewset: type[BasePrefixableGenericViewSet[Model] | BasePrefixableViewSet]
    for viewset in VIEWSETS:
        no_basename_exception: AssertionError
        try:
            router.register(viewset.PREFIX, viewset)
        except AssertionError as no_basename_exception:
            if "`basename` argument not specified" in str(no_basename_exception):
                router.register(
                    viewset.PREFIX.lower(),
                    viewset,
                    basename=viewset.PREFIX.lower().rstrip("s"),
                )
            else:
                raise no_basename_exception from no_basename_exception

    return router


urlpatterns: MutableSequence[URLResolver | URLPattern] = [
    django.urls.path(r"", django.urls.include(create_router().urls)),
    django.urls.path(
        r"my-user-details/",
        MyUserDetailsView.as_view(),
        name="my_user_details",
    ),
]
