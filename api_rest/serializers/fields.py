"""Custom Serializer fields for REST API."""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "RelatedToolTagField",
    "RelatedTopicTagField",
    "RelatedOtherTagField",
)

from typing import override

from django.db.models import QuerySet
from rest_framework.relations import SlugRelatedField

from ratemymodule.models import OtherTag, ToolTag, TopicTag


class RelatedToolTagField(SlugRelatedField[ToolTag]):
    """Field for displaying a Post's ToolTags."""

    # noinspection PyOverrides
    @override
    def get_queryset(self) -> QuerySet[ToolTag]:
        """Return the viewable queryset of ToolTags."""
        if not self.context["request"].user.is_staff:
            return ToolTag.objects.filter(is_verified=True)

        return ToolTag.objects.all()


class RelatedTopicTagField(SlugRelatedField[TopicTag]):
    """Field for displaying a Post's TopicTags."""

    # noinspection PyOverrides
    @override
    def get_queryset(self) -> QuerySet[TopicTag]:
        """Return the viewable queryset of TopicTags."""
        if not self.context["request"].user.is_staff:
            return TopicTag.objects.filter(is_verified=True)

        return TopicTag.objects.all()


class RelatedOtherTagField(SlugRelatedField[OtherTag]):
    """Field for displaying a Post's OtherTags."""

    # noinspection PyOverrides
    @override
    def get_queryset(self) -> QuerySet[OtherTag]:
        """Return the viewable queryset of OtherTags."""
        if not self.context["request"].user.is_staff:
            return OtherTag.objects.filter(is_verified=True)

        return OtherTag.objects.all()
