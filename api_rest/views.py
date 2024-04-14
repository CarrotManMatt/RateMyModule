"""REST API views for `RateMyModule` project."""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "CustomAPIRootView",
    "BasePrefixableGenericViewSet",
    "BasePrefixableViewSet",
    "UserViewSet",
    "MyUserDetailsView",
    "UniversityViewSet",
    "CourseViewSet",
    "ModuleViewSet",
    "ToolTagViewSet",
    "TopicTagViewSet",
    "OtherTagViewSet",
    "PostViewSet",
    "ReportViewSet",
)

import abc
import contextlib
from typing import TYPE_CHECKING, Final, TypeVar, override

import rest_framework
from django.db.models import Model, QuerySet
from django.urls import NoReverseMatch
from rest_framework.permissions import (
    DjangoModelPermissions,
    DjangoModelPermissionsOrAnonReadOnly,
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet, ViewSet

from api_rest.serializers import (
    CourseSerializer,
    ModuleSerializer,
    OtherTagSerializer,
    PostSerializer,
    ReportSerializer,
    ToolTagSerializer,
    TopicTagSerializer,
    UniversitySerializer,
    UserSerializer,
)
from ratemymodule.models import (
    Course,
    Module,
    OtherTag,
    Post,
    Report,
    ToolTag,
    TopicTag,
    University,
    User,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import AnonymousUser
    from rest_framework import reverse  # noqa: F401


model_T = TypeVar("model_T", bound=Model)  # noqa: N816


class CustomAPIRootView(APIRootView):
    @override
    def get_view_name(self) -> str:
        return "API Root"

    # noinspection PyShadowingBuiltins,PyMethodOverriding
    @override
    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        if request.resolver_match is None:
            raise RuntimeError
        namespace: str = request.resolver_match.namespace

        reverse_format: object = kwargs.get("format")
        if reverse_format is not None and not isinstance(reverse_format, str):
            INVALID_FORMAT_TYPE_MESSAGE: Final[str] = (
                "'format' parameter must be of type str or None."
            )
            raise TypeError(INVALID_FORMAT_TYPE_MESSAGE)

        ret: dict[str, str] = {}

        api_root_dict: dict[str, str] = (
            self.api_root_dict.copy() if self.api_root_dict is not None else {}
        )

        if not request.user.is_staff:
            api_root_dict.pop(UserViewSet.PREFIX, None)
            api_root_dict.pop(ReportViewSet.PREFIX, None)

        if request.user.is_authenticated:
            with contextlib.suppress(NoReverseMatch):
                # noinspection PyUnresolvedReferences
                ret["my_user_details"] = rest_framework.reverse.reverse(
                    f"{namespace}:my_user_details" if namespace else "my_user_details",
                    request=request,
                    format=reverse_format,
                )

        key: str
        url_name: str
        for key, url_name in api_root_dict.items():
            try:
                ret[key] = rest_framework.reverse.reverse(
                    namespace + ":" + url_name if namespace else url_name,
                    args=args,
                    kwargs=kwargs,
                    request=request,
                    format=reverse_format,
                )
            except NoReverseMatch:
                # NOTE: Don't bail out if eg. no list routes exist, only detail routes.
                continue

        return Response(ret)


class BasePrefixableGenericViewSet(GenericViewSet[model_T], abc.ABC):
    PREFIX: str


class BasePrefixableViewSet(ViewSet, abc.ABC):
    PREFIX: str


class PrefixableReadOnlyModelViewSet(ReadOnlyModelViewSet[model_T], BasePrefixableGenericViewSet[model_T], abc.ABC):  # noqa: E501
    pass


class PrefixableModelViewSet(ModelViewSet[model_T], BasePrefixableGenericViewSet[model_T], abc.ABC):  # noqa: E501
    pass


class UserViewSet(PrefixableReadOnlyModelViewSet[User]):
    PREFIX: str = r"users"

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser, DjangoModelPermissions)


class MyUserDetailsView(APIView):
    permission_classes = (IsAuthenticated,)

    # noinspection PyOverrides
    @override
    def get(self, request: Request) -> Response:  # type: ignore[misc]
        user: User | AnonymousUser = request.user
        if not user.is_authenticated or not isinstance(user, User):
            USER_NOT_AUTHENTICATED_MESSAGE: Final[str] = "User is not authenticated"
            raise TypeError(USER_NOT_AUTHENTICATED_MESSAGE)

        return Response(UserSerializer(user, context={"request": request}).data)


class UniversityViewSet(PrefixableModelViewSet[University]):
    PREFIX: str = r"universities"

    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)


class CourseViewSet(PrefixableModelViewSet[Course]):
    PREFIX: str = r"courses"

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)


class ModuleViewSet(PrefixableModelViewSet[Module]):
    PREFIX: str = r"modules"

    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)


class ToolTagViewSet(PrefixableModelViewSet[ToolTag]):
    PREFIX: str = r"tool-tags"

    queryset = ToolTag.objects.all()
    serializer_class = ToolTagSerializer

    def get_queryset(self) -> QuerySet[ToolTag]:
        if not self.request.user.is_staff:
            return super().get_queryset().filter(is_verified=True)

        return super().get_queryset()


class TopicTagViewSet(PrefixableModelViewSet[TopicTag]):
    PREFIX: str = r"topic-tags"

    queryset = TopicTag.objects.all()
    serializer_class = TopicTagSerializer

    def get_queryset(self) -> QuerySet[TopicTag]:
        if not self.request.user.is_staff:
            return super().get_queryset().filter(is_verified=True)

        return super().get_queryset()


class OtherTagViewSet(PrefixableModelViewSet[OtherTag]):
    PREFIX: str = r"other-tags"

    queryset = OtherTag.objects.all()
    serializer_class = OtherTagSerializer

    def get_queryset(self) -> QuerySet[OtherTag]:
        if not self.request.user.is_staff:
            return super().get_queryset().filter(is_verified=True)

        return super().get_queryset()


class PostViewSet(PrefixableModelViewSet[Post]):
    PREFIX: str = r"posts"

    serializer_class = PostSerializer

    def get_queryset(self) -> QuerySet[Post]:
        return Post.filter_by_viewable(request=self.request).all()


class ReportViewSet(PrefixableModelViewSet[Report]):
    PREFIX: str = r"reports"

    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = (IsAdminUser, DjangoModelPermissions)
