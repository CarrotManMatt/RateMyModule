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
    # noinspection PyOverrides
    @override
    def get_queryset(self) -> QuerySet[ToolTag]:
        if not self.context["request"].user.is_staff:
            return ToolTag.objects.filter(is_verified=True)

        return ToolTag.objects.all()


class RelatedTopicTagField(SlugRelatedField[TopicTag]):
    # noinspection PyOverrides
    @override
    def get_queryset(self) -> QuerySet[TopicTag]:
        if not self.context["request"].user.is_staff:
            return TopicTag.objects.filter(is_verified=True)

        return TopicTag.objects.all()


class RelatedOtherTagField(SlugRelatedField[OtherTag]):
    # noinspection PyOverrides
    @override
    def get_queryset(self) -> QuerySet[OtherTag]:
        if not self.context["request"].user.is_staff:
            return OtherTag.objects.filter(is_verified=True)

        return OtherTag.objects.all()
