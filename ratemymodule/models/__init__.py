"""Model classes within `ratemymodule` app."""

from collections.abc import Sequence

__all__: Sequence[str] = ("User",)

from collections.abc import Set as ImmutableSet
from datetime import datetime
from typing import TYPE_CHECKING, Final, override

from allauth.account.models import EmailAddress
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager
from .utils import AttributeDeleter, CustomBaseModel
from .validators import (
    ConfusableEmailValidator,
    ExampleEmailValidator,
    FreeEmailValidator,
    HTML5EmailValidator,
    PreexistingEmailTLDValidator,
)

if TYPE_CHECKING:
    from django.contrib.contenttypes.fields import GenericForeignKey
    from django.db.models import ForeignObjectRel


class User(CustomBaseModel, AbstractBaseUser, PermissionsMixin):
    """Primary model class for users that can create an account & log into it."""

    normalize_username = AttributeDeleter(  # type: ignore[assignment]
        object_name="User",
        attribute_name="normalize_username"
    )

    email = models.EmailField(
        verbose_name=_("Email Address"),
        max_length=255,
        unique=True,
        validators=[
            HTML5EmailValidator(),
            FreeEmailValidator(),
            ConfusableEmailValidator(),
            PreexistingEmailTLDValidator(),
            ExampleEmailValidator()
        ],
        error_messages={
            "unique": _("A user with that Email Address already exists."),
            "max_length": _("The Email Address must be at most 255 digits.")
        }
    )
    is_staff = models.BooleanField(
        _("Is Admin?"),
        default=False,
        help_text=_("Designates whether the user can log into the admin site.")
    )
    is_active = models.BooleanField(
        _("Is Active?"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        )
    )
    # liked_post_set = models.ManyToManyField(
    #     "Post",
    #     related_name="liked_by_users",
    #     verbose_name=_("Liked Posts"),
    #     help_text=_("The set of posts this user has liked."),
    #     blank=True
    # )
    # disliked_post_set = models.ManyToManyField(
    #     "Post",
    #     related_name="disliked_by_users",
    #     verbose_name=_("Disliked Posts"),
    #     help_text=_("The set of posts this user has disliked."),
    #     blank=True
    # )
    # enrolled_course_set = models.ManyToManyField(
    #     "Course",
    #     related_name="enrolled_users",
    #     verbose_name=_("Enrolled Courses"),
    #     help_text=_("The set of courses this user has enrolled in."),
    #     blank=False
    # )

    objects = UserManager()
    # noinspection SpellCheckingInspection
    emailaddress_set: models.Manager[EmailAddress]  # type: ignore[no-any-unimported]
    # made_post_set: models.Manager[Post]
    # made_report_set: models.Manager[Report]

    USERNAME_FIELD: Final[str] = "email"
    EMAIL_FIELD: Final[str] = "email"

    @property
    def date_time_joined(self) -> datetime:
        """Shorcut accessor to the time this `User` object was created."""
        return self.date_time_created

    @date_time_joined.setter
    def date_time_joined(self, value: datetime) -> None:
        self.date_time_created = value

    # @property
    # def university(self) -> University:
    #     return self.enrolled_course_set.first().university

    class Meta:
        """Metadata options about this model."""

        verbose_name = _("User")

    @override
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        password_field: models.Field[object, object] | ForeignObjectRel | GenericForeignKey = (
            self._meta.get_field("password")
        )
        if isinstance(password_field, models.Field):
            password_field.error_messages = {
                "null": _("Password is a required field."),
                "blank": _("Password is a required field.")
            }
        is_superuser_field: models.Field[object, object] | ForeignObjectRel | GenericForeignKey = (  # noqa: E501
            self._meta.get_field("is_superuser")
        )
        if isinstance(is_superuser_field, models.Field):
            is_superuser_field.verbose_name = _("Is Superuser?")

    @override
    def __str__(self) -> str:
        return self.email

    @override
    def clean(self) -> None:
        if self.is_superuser:
            self.is_staff = True

        # TODO: Also signal when adding new course to user & vice-versa
        # if self.enrolled_course_set.exclude(university=self.university).exists():
        #     raise ValidationError(
        #         {
        #             "university":
        #                 "This user is linked to courses across multiple universities."
        #         },
        #         code="invalid"
        #     )

        # TODO: University email validator upon signup
        # TODO: Validate like & unlike a post (no conflicts)
        # TODO: Validate courses not empty

    @classmethod
    @override
    def get_proxy_field_names(cls) -> ImmutableSet[str]:
        return super().get_proxy_field_names() | {"date_time_joined"}

    # def like_post(self, post: Post) -> None:  # TODO: Also signals
    #     self.undislike_post(post=post)
    #     self.liked_post_set.add(post)
    #
    # def dislike_post(self, post: Post) -> None:
    #     self.unlike_post(post=post)
    #     self.liked_post_set.add(post)
    #
    # def unlike_post(self, post: Post) -> None:
    #     self.liked_post_set.remove(post)
    #
    # def undislike_post(self, post: Post) -> None:
    #     self.disliked_post_set.remove(post)
