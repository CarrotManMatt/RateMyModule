"""Model serializers for REST API."""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "UserSerializer",
    "UniversitySerializer",
    "CourseSerializer",
    "ModuleSerializer",
    "ToolTagSerializer",
    "TopicTagSerializer",
    "OtherTagSerializer",
    "PostSerializer",
    "ReportSerializer",
)

from collections.abc import Callable, Iterable
from typing import Final, override

from django_stubs_ext import StrOrPromise
from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import (
    HyperlinkedModelSerializer,
    HyperlinkedRelatedField,
    ModelSerializer,
)

from ratemymodule.models import (
    BaseTag,
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

from .fields import RelatedOtherTagField, RelatedToolTagField, RelatedTopicTagField


class UserSerializer(HyperlinkedModelSerializer):
    """A class for serializing users."""

    university: HyperlinkedRelatedField[University] = HyperlinkedRelatedField(
        read_only=True,
        view_name="api_rest:university-detail",
    )
    password_hash: serializers.CharField = serializers.CharField(
        source="password",
        read_only=True,
    )

    class Meta:  # noqa: D106
        model = User
        # noinspection PyUnresolvedReferences
        fields = (
            "url",
            "email",
            "short_username",
            "is_staff",
            "is_superuser",
            "password_hash",
            "university",
            "enrolled_course_set",
            "liked_post_set",
            "disliked_post_set",
            "made_post_set",
            "made_report_set",
            "date_time_joined",
            "last_login",
        )
        # noinspection PyUnresolvedReferences
        extra_kwargs = {  # noqa: RUF012
            "url": {"view_name": "api_rest:user-detail"},
            "university": {"view_name": "api_rest:university-detail"},
            "enrolled_course_set": {"view_name": "api_rest:course-detail"},
            "liked_post_set": {"view_name": "api_rest:post-detail"},
            "disliked_post_set": {"view_name": "api_rest:post-detail"},
            "made_post_set": {"view_name": "api_rest:post-detail"},
            "made_report_set": {"view_name": "api_rest:report-detail"},
        }

    # noinspection PyOverrides
    @override
    def __init__(self, instance: User | None = None, data: User | empty = empty, *, partial: bool = False, many: bool = False, context: dict[str, object] | None = None, read_only: bool = False, write_only: bool = False, required: bool | None = None, default: User | empty = empty, initial: User | empty = empty, source: str | None = None, label: StrOrPromise | None = None, help_text: StrOrPromise | None = None, style: dict[str, object] | None = None, error_messages: dict[str, StrOrPromise] | None = None, validators: Sequence[Callable[[object], None]] | None = None, allow_null: bool = False) -> None:  # type: ignore[valid-type] # noqa: E501
        super().__init__(
            instance=instance,
            data=data,
            partial=partial,
            many=many,
            context=context or {},
            read_only=read_only,
            write_only=write_only,
            required=required,
            default=default,
            initial=initial,
            source=source,
            label=label,
            help_text=help_text,
            style=style,
            error_messages=error_messages,
            validators=validators,
            allow_null=allow_null,
        )

        if not self.context["request"].user.is_superuser:
            superuser_field_name: str
            for superuser_field_name in ("is_superuser",):
                self.fields.pop(superuser_field_name, None)

        if not self.context["request"].user.is_staff:
            staff_field_name: str
            for staff_field_name in ("url", "password_hash", "is_staff", "last_login"):
                self.fields.pop(staff_field_name, None)


class UniversitySerializer(HyperlinkedModelSerializer):
    """A class for serializing universities."""

    module_set: HyperlinkedRelatedField[Module] = HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name="api_rest:module-detail",
    )

    class Meta:  # noqa: D106
        model = University
        # noinspection PyUnresolvedReferences
        fields = (
            "url",
            "name",
            "short_name",
            "founding_date",
            "course_set",
            "module_set",
            "date_time_created",
        )
        # noinspection PyUnresolvedReferences
        extra_kwargs = {  # noqa: RUF012
            "url": {"view_name": "api_rest:university-detail"},
            "course_set": {"view_name": "api_rest:course-detail"},
        }

    # noinspection PyOverrides
    @override
    def __init__(self, instance: University | None = None, data: University | empty = empty, *, partial: bool = False, many: bool = False, context: dict[str, object] | None = None, read_only: bool = False, write_only: bool = False, required: bool | None = None, default: University | empty = empty, initial: University | empty = empty, source: str | None = None, label: StrOrPromise | None = None, help_text: StrOrPromise | None = None, style: dict[str, object] | None = None, error_messages: dict[str, StrOrPromise] | None = None, validators: Sequence[Callable[[object], None]] | None = None, allow_null: bool = False) -> None:  # type: ignore[valid-type] # noqa: E501
        super().__init__(
            instance=instance,
            data=data,
            partial=partial,
            many=many,
            context=context or {},
            read_only=read_only,
            write_only=write_only,
            required=required,
            default=default,
            initial=initial,
            source=source,
            label=label,
            help_text=help_text,
            style=style,
            error_messages=error_messages,
            validators=validators,
            allow_null=allow_null,
        )

        if not self.context["request"].user.is_staff:
            staff_field_name: str
            for staff_field_name in ("date_time_created",):
                self.fields.pop(staff_field_name, None)


class CourseSerializer(HyperlinkedModelSerializer):
    """A class for serializing courses."""

    class Meta:  # noqa: D106
        model = Course
        # noinspection PyUnresolvedReferences
        fields = (
            "url",
            "name",
            "student_type",
            "university",
            "module_set",
            "enrolled_user_set",
            "date_time_created",
        )
        # noinspection PyUnresolvedReferences
        extra_kwargs = {  # noqa: RUF012
            "url": {"view_name": "api_rest:course-detail"},
            "university": {"view_name": "api_rest:university-detail"},
            "module_set": {"view_name": "api_rest:module-detail"},
            "enrolled_user_set": {"view_name": "api_rest:user-detail"},
        }

    # noinspection PyOverrides
    @override
    def __init__(self, instance: Course | None = None, data: Course | empty = empty, *, partial: bool = False, many: bool = False, context: dict[str, object] | None = None, read_only: bool = False, write_only: bool = False, required: bool | None = None, default: Course | empty = empty, initial: Course | empty = empty, source: str | None = None, label: StrOrPromise | None = None, help_text: StrOrPromise | None = None, style: dict[str, object] | None = None, error_messages: dict[str, StrOrPromise] | None = None, validators: Sequence[Callable[[object], None]] | None = None, allow_null: bool = False) -> None:  # type: ignore[valid-type] # noqa: E501
        super().__init__(
            instance=instance,
            data=data,
            partial=partial,
            many=many,
            context=context or {},
            read_only=read_only,
            write_only=write_only,
            required=required,
            default=default,
            initial=initial,
            source=source,
            label=label,
            help_text=help_text,
            style=style,
            error_messages=error_messages,
            validators=validators,
            allow_null=allow_null,
        )

        if not self.context["request"].user.is_staff:
            staff_field_name: str
            for staff_field_name in ("enrolled_user_set", "date_time_created"):
                self.fields.pop(staff_field_name, None)


class ModuleSerializer(HyperlinkedModelSerializer):
    """A class for serializing Modules."""

    university: HyperlinkedRelatedField[University] = HyperlinkedRelatedField(
        read_only=True,
        view_name="api_rest:university-detail",
    )
    web_url: serializers.SerializerMethodField = serializers.SerializerMethodField()
    year_started: serializers.SerializerMethodField = serializers.SerializerMethodField()
    date_started: serializers.CharField = serializers.CharField(
        source="year_started",
    )

    class Meta:  # noqa: D106
        model = Module
        # noinspection PyUnresolvedReferences
        fields = (
            "url",
            "name",
            "code",
            "year_started",
            "date_started",
            "web_url",
            "university",
            "course_set",
            "post_set",
            "date_time_created",
        )
        # noinspection PyUnresolvedReferences
        extra_kwargs = {  # noqa: RUF012
            "url": {"view_name": "api_rest:module-detail"},
            "course_set": {"view_name": "api_rest:course-detail"},
            "post_set": {"view_name": "api_rest:post-detail"},
        }

    # noinspection PyOverrides
    @override
    def __init__(self, instance: Module | None = None, data: Module | empty = empty, *, partial: bool = False, many: bool = False, context: dict[str, object] | None = None, read_only: bool = False, write_only: bool = False, required: bool | None = None, default: Module | empty = empty, initial: Module | empty = empty, source: str | None = None, label: StrOrPromise | None = None, help_text: StrOrPromise | None = None, style: dict[str, object] | None = None, error_messages: dict[str, StrOrPromise] | None = None, validators: Sequence[Callable[[object], None]] | None = None, allow_null: bool = False) -> None:  # type: ignore[valid-type] # noqa: E501
        super().__init__(
            instance=instance,
            data=data,
            partial=partial,
            many=many,
            context=context or {},
            read_only=read_only,
            write_only=write_only,
            required=required,
            default=default,
            initial=initial,
            source=source,
            label=label,
            help_text=help_text,
            style=style,
            error_messages=error_messages,
            validators=validators,
            allow_null=allow_null,
        )

        if not self.context["request"].user.is_staff:
            staff_field_name: str
            for staff_field_name in ("date_started", "date_time_created"):
                self.fields.pop(staff_field_name, None)

    # noinspection PyOverrides
    @override
    def get_web_url(self, obj: Module) -> str:  # type: ignore[misc]
        return self.context["request"].build_absolute_uri(obj.get_absolute_url())  # type: ignore[no-any-return]

    # noinspection PyOverrides
    @override
    def get_year_started(self, obj: Module) -> int:  # type: ignore[misc]
        return obj.year_started.year


class _BaseTagSerializer(ModelSerializer[BaseTag]):
    # noinspection PyOverrides
    @override
    def __init__(self, instance: BaseTag | None = None, data: BaseTag | empty = empty, *, partial: bool = False, many: bool = False, context: dict[str, object] | None = None, read_only: bool = False, write_only: bool = False, required: bool | None = None, default: BaseTag | empty = empty, initial: BaseTag | empty = empty, source: str | None = None, label: StrOrPromise | None = None, help_text: StrOrPromise | None = None, style: dict[str, object] | None = None, error_messages: dict[str, StrOrPromise] | None = None, validators: Sequence[Callable[[object], None]] | None = None, allow_null: bool = False) -> None:  # type: ignore[valid-type] # noqa: E501
        super().__init__(
            instance=instance,
            data=data,
            partial=partial,
            many=many,
            context=context or {},
            read_only=read_only,
            write_only=write_only,
            required=required,
            default=default,
            initial=initial,
            source=source,
            label=label,
            help_text=help_text,
            style=style,
            error_messages=error_messages,
            validators=validators,
            allow_null=allow_null,
        )

        if not self.context["request"].user.is_staff:
            staff_field_name: str
            for staff_field_name in ("is_verified",):
                self.fields.pop(staff_field_name, None)


class ToolTagSerializer(HyperlinkedModelSerializer):
    """A class for serializing Tool Tags."""

    class Meta:  # noqa: D106
        model = ToolTag
        # noinspection PyUnresolvedReferences
        fields = (
            "url",
            "name",
            "is_verified",
        )
        # noinspection PyUnresolvedReferences
        extra_kwargs = {"url": {"view_name": "api_rest:tooltag-detail"}}  # noqa: RUF012


class TopicTagSerializer(HyperlinkedModelSerializer):
    """A class for serializing topic tags."""

    class Meta:  # noqa: D106
        model = TopicTag
        # noinspection PyUnresolvedReferences
        fields = (
            "url",
            "name",
            "is_verified",
        )
        # noinspection PyUnresolvedReferences
        extra_kwargs = {"url": {"view_name": "api_rest:topictag-detail"}}  # noqa: RUF012


class OtherTagSerializer(HyperlinkedModelSerializer):
    """A class for serializing other tags."""

    class Meta:  # noqa: D106
        model = OtherTag
        # noinspection PyUnresolvedReferences
        fields = (
            "url",
            "name",
            "is_verified",
        )
        # noinspection PyUnresolvedReferences
        extra_kwargs = {"url": {"view_name": "api_rest:othertag-detail"}}  # noqa: RUF012


class PostSerializer(HyperlinkedModelSerializer):
    """A class for serializing Posts."""

    user_display: serializers.CharField = serializers.CharField(
        read_only=True,
        source="display_user",
    )
    liked_by_me: serializers.SerializerMethodField = serializers.SerializerMethodField()
    disliked_by_me: serializers.SerializerMethodField = serializers.SerializerMethodField()
    user_url: HyperlinkedRelatedField[User] = HyperlinkedRelatedField(
        view_name="api_rest:user-detail",
        source="user",
        queryset=User.objects.all(),
    )
    tool_tag_set: SlugRelatedField[ToolTag] = RelatedToolTagField(many=True, slug_field="name")
    topic_tag_set: SlugRelatedField[TopicTag] = RelatedTopicTagField(
        many=True,
        slug_field="name",
    )
    other_tag_set: SlugRelatedField[OtherTag] = RelatedOtherTagField(
        many=True,
        slug_field="name",
    )

    class Meta:  # noqa: D106
        model = Post
        # noinspection PyUnresolvedReferences
        fields = (
            "url",
            "module",
            "user_display",
            "user_url",
            "overall_rating",
            "difficulty_rating",
            "assessment_rating",
            "teaching_rating",
            "content",
            "tool_tag_set",
            "topic_tag_set",
            "other_tag_set",
            "date_time_posted",
            "liked_by_me",
            "disliked_by_me",
            "overall_likes_count",
            "likes_count",
            "dislikes_count",
            "liked_user_set",
            "disliked_user_set",
            "academic_year_start",
            "is_user_suspicious",
            "report_set",
            "hidden",
        )
        # noinspection PyUnresolvedReferences
        extra_kwargs = {  # noqa: RUF012
            "url": {"view_name": "api_rest:post-detail"},
            "module": {"view_name": "api_rest:module-detail"},
            "liked_user_set": {"view_name": "api_rest:user-detail"},
            "disliked_user_set": {"view_name": "api_rest:user-detail"},
            "report_set": {"view_name": "api_rest:report-detail"},
        }

    # noinspection PyOverrides
    @override
    def __init__(self, instance: Post | None = None, data: Post | empty = empty, *, partial: bool = False, many: bool = False, context: dict[str, object] | None = None, read_only: bool = False, write_only: bool = False, required: bool | None = None, default: Post | empty = empty, initial: Post | empty = empty, source: str | None = None, label: StrOrPromise | None = None, help_text: StrOrPromise | None = None, style: dict[str, object] | None = None, error_messages: dict[str, StrOrPromise] | None = None, validators: Sequence[Callable[[object], None]] | None = None, allow_null: bool = False) -> None:  # type: ignore[valid-type] # noqa: E501
        super().__init__(
            instance=instance,
            data=data,
            partial=partial,
            many=many,
            context=context or {},
            read_only=read_only,
            write_only=write_only,
            required=required,
            default=default,
            initial=initial,
            source=source,
            label=label,
            help_text=help_text,
            style=style,
            error_messages=error_messages,
            validators=validators,
            allow_null=allow_null,
        )

        if not self.context["request"].user.is_staff:
            STAFF_FIELD_NAMES: Final[Iterable[str]] = (
                "user_url",
                "likes_count",
                "dislikes_count",
                "liked_user_set",
                "disliked_user_set",
                "report_set",
                "hidden",
            )
            staff_field_name: str
            for staff_field_name in STAFF_FIELD_NAMES:
                self.fields.pop(staff_field_name, None)

    # noinspection PyOverrides
    @override
    def get_liked_by_me(self, obj: Post) -> bool:  # type: ignore[misc]
        if not self.context["request"].user.is_authenticated:
            return False

        return self.context["request"].user in obj.liked_user_set.all()

    # noinspection PyOverrides
    @override
    def get_disliked_by_me(self, obj: Post) -> bool:  # type: ignore[misc]
        if not self.context["request"].user.is_authenticated:
            return False

        return self.context["request"].user in obj.disliked_user_set.all()


class ReportSerializer(HyperlinkedModelSerializer):
    """A class for serializing reports."""

    class Meta:  # noqa: D106
        model = Report
        # noinspection PyUnresolvedReferences
        fields = (
            "url",
            "post",
            "reporter",
            "reason",
            "is_solved",
            "date_time_created",
        )
        # noinspection PyUnresolvedReferences
        extra_kwargs = {  # noqa: RUF012
            "url": {"view_name": "api_rest:report-detail"},
            "post": {"view_name": "api_rest:post-detail"},
            "reporter": {"view_name": "api_rest:user-detail"},
        }
