"""Model classes within `ratemymodule` app."""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "User",
    "University",
    "Course",
    "Module",
    "BaseTag",
    "ToolTag",
    "TopicTag",
    "OtherTag",
    "Post",
    "Report"
)

from collections.abc import Set as ImmutableSet
from datetime import datetime
from typing import TYPE_CHECKING, Final, override

from allauth.account.models import EmailAddress
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinLengthValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.db.models.manager import RelatedManager

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
    liked_post_set = models.ManyToManyField(
        "ratemymodule.Post",
        related_name="liked_by_users",
        verbose_name=_("Liked Posts"),
        help_text=_("The set of posts this user has liked."),
        blank=True
    )
    disliked_post_set = models.ManyToManyField(
        "ratemymodule.Post",
        related_name="disliked_by_users",
        verbose_name=_("Disliked Posts"),
        help_text=_("The set of posts this user has disliked."),
        blank=True
    )
    enrolled_course_set = models.ManyToManyField(
        "ratemymodule.Course",
        related_name="enrolled_users",
        verbose_name=_("Enrolled Courses"),
        help_text=_("The set of courses this user has enrolled in."),
        blank=False
    )

    objects = UserManager()
    # noinspection SpellCheckingInspection
    emailaddress_set: RelatedManager[EmailAddress]  # type: ignore[no-any-unimported]
    made_post_set: RelatedManager["Post"]
    made_report_set: RelatedManager["Report"]

    USERNAME_FIELD: Final[str] = "email"
    EMAIL_FIELD: Final[str] = "email"

    @property
    def date_time_joined(self) -> datetime:
        """Shortcut accessor to the time this `User` object was created."""
        return self.date_time_created

    @date_time_joined.setter
    def date_time_joined(self, __value: datetime) -> None:
        self.date_time_created = __value

    @property
    def university(self) -> "University":
        """Shortcut accessor to the university this user is a student at."""
        first_enrolled_course: Course | None = self.enrolled_course_set.first()
        if not first_enrolled_course:
            raise Course.DoesNotExist

        return first_enrolled_course.university

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
        if self.enrolled_course_set.exclude(university=self.university).exists():
            raise ValidationError(
                {
                    "university":
                        "This user is linked to courses across multiple universities."
                },
                code="invalid"
            )

        # TODO: University email validator upon signup
        # TODO: Validate like & unlike a post (no conflicts)
        # TODO: Validate courses not empty

    @classmethod
    @override
    def get_proxy_field_names(cls) -> ImmutableSet[str]:
        return super().get_proxy_field_names() | {"date_time_joined"}

    def like_post(self, post: "Post") -> None:  # TODO: Also signals
        """Like a given post, by this user, ensuring it's not disliked at the same time."""
        self.unlike_post(post=post)
        self.liked_post_set.add(post)

    def dislike_post(self, post: "Post") -> None:
        """Dislike a given post, by this user, ensuring it's not liked at the same time."""
        self.unlike_post(post=post)
        self.liked_post_set.add(post)

    def unlike_post(self, post: "Post") -> None:
        """Remove like and dislike from a given post, for this user."""
        self.liked_post_set.remove(post)
        self.disliked_post_set.remove(post)


class University(CustomBaseModel):
    """Model class for universities that have many courses."""

    name = models.CharField(
        max_length=60,
        unique=True,
        verbose_name=_("Name"),
        validators=[MinLengthValidator(2)]
    )
    short_name = models.CharField(
        max_length=5,
        unique=False,
        verbose_name=_("Short Name"),
        validators=[MinLengthValidator(2)]
    )
    email_domain = models.CharField(
        max_length=253,
        unique=True,
        verbose_name=_("Email Domain")
    )
    founding_date = models.DateField(
        verbose_name=_("Date Founded"),
        help_text=_("Date format DD/MM/YYYY")
    )

    course_set: RelatedManager["Course"]

    class Meta:
        """Metadata options about this model."""

        verbose_name = _("University")

    @override
    def __str__(self) -> str:
        return self.name


class Course(CustomBaseModel):
    """Model class for Courses that users can be enrolled in."""

    name = models.CharField(
        max_length=60,
        verbose_name=_("Name")
    )
    student_type = models.CharField(
        max_length=60,
        verbose_name=_("Student Type")
    )
    university = models.ForeignKey(
        University,
        related_name="course_set",
        verbose_name=_("University"),
        on_delete=models.PROTECT,
        help_text=_("The university that this course is taught at")
    )

    module_set: RelatedManager["Module"]

    class Meta:
        """Metadata options about this model."""

        verbose_name = _("Course")

    @override
    def __str__(self) -> str:
        return self.name


class Module(CustomBaseModel):
    """Model class for modules that can have posts made about them."""

    name = models.CharField(
        max_length=60,
        verbose_name=_("Name"),
    )
    year_started = models.DateField(
        verbose_name=_("Year Started"),
        help_text=_("Date format DD/MM/YYYY")
    )
    code = models.CharField(
        max_length=60,
        unique=True,
        verbose_name=_("Reference Code"),
        help_text=_("The unique reference code of this module within its university")
    )
    course_set = models.ManyToManyField(
        Course,
        related_name="module_set",
        verbose_name=_("Attached Courses"),
        help_text=_("The set of courses that can include this module"),
    )

    class Meta:
        """Metadata options about this model."""

        verbose_name = _("Module")

    @override
    def get_absolute_url(self) -> str:
        # TODO: Implement function to get absolute URL
        raise NotImplementedError

    @override
    def __str__(self) -> str:
        return self.name


class BaseTag(CustomBaseModel):
    """Base model class for tags that can be added to posts."""

    name = models.CharField(
        max_length=60,
        unique=True,
        verbose_name=_("Tag Name"),
        validators=[MinLengthValidator(2)]
    )
    is_verified = models.BooleanField(default=False, verbose_name=_("Is Verified?"))

    class Meta:
        """Metadata options about this model."""

        abstract = True

    @override
    def __str__(self) -> str:
        return self.name


class TopicTag(BaseTag):
    """Model class for tags about the topics within a module, that can be added to posts."""

    class Meta:
        """Metadata options about this model."""

        verbose_name = _("Topic Tag")


class OtherTag(BaseTag):
    """Model class for other tags describing a module, that can be added to posts."""

    class Meta:
        """Metadata options about this model."""

        verbose_name = _("Other Tag")


class ToolTag(BaseTag):
    """Model class for tags about the tools used in a module, that can be added to posts."""

    class Meta:
        """Metadata options about this model."""

        verbose_name = _("Tool Tag")


class Post(CustomBaseModel):
    """Core model class for posts that can be made by users about modules."""

    class Rating(models.IntegerChoices):
        """Enum of star rating numbers."""

        ZERO = 0, "0"
        ONE = 1, "1"
        TWO = 2, "2"
        THREE = 3, "3"
        FOUR = 4, "4"
        FIVE = 5, "5"

    module = models.ForeignKey(
        Module,
        on_delete=models.PROTECT,
        related_name="post_set",
        verbose_name=_("Module")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="made_post_set",
        verbose_name=_("User")
    )

    overall_rating = models.IntegerField(
        choices=Rating.choices,
        verbose_name=_("Overall Rating")
    )
    difficulty_rating = models.IntegerField(
        choices=Rating.choices,
        verbose_name=_("Difficulty Rating")
    )
    assessment_rating = models.IntegerField(
        choices=Rating.choices,
        verbose_name=_("Assessment Rating")
    )
    teaching_rating = models.IntegerField(
        choices=Rating.choices,
        verbose_name=_("Teaching Rating")
    )
    content = models.TextField(verbose_name=_("Content"))
    academic_year_start = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1000),
            MaxValueValidator(3000)
        ],
        verbose_name=_("Academic Year Start")
    )
    hidden = models.BooleanField(default=False, verbose_name=_("Is Hidden?"))

    other_tag_set = models.ManyToManyField(
        OtherTag,
        blank=True,
        related_name="post_set",
        verbose_name=_("Other Tags")
    )
    tool_tag_set = models.ManyToManyField(
        ToolTag,
        blank=True,
        related_name="post_set",
        verbose_name=_("Tool Tags")
    )
    topic_tag_set = models.ManyToManyField(
        TopicTag,
        blank=True,
        related_name="post_set",
        verbose_name=_("Topic Tags")
    )

    report_set: RelatedManager["Report"]
    liked_user_set: RelatedManager[User]
    disliked_user_set: RelatedManager[User]

    class Meta:
        """Metadata options about this model."""

        verbose_name = _("Post")

    @classmethod
    @override
    def get_proxy_field_names(cls) -> ImmutableSet[str]:
        return super().get_proxy_field_names() | {"date_time_posted"}

    @property
    def date_time_posted(self) -> datetime:
        """Shortcut accessor to the time this `Post` object was created."""
        return self.date_time_created

    @date_time_posted.setter
    def date_time_posted(self, __value: datetime) -> None:
        self.date_time_created = __value

    @property
    def liked_count(self) -> int:
        """The number of likes this post has."""
        return self.liked_user_set.count()

    @property
    def disliked_count(self) -> int:
        """The number of dislikes this post has."""
        return self.disliked_user_set.count()

    # Methods to handle post liking and unliking logic
    def user_like(self, user: User) -> None:
        """Like this post, for a given user, ensuring it's not disliked at the same time."""
        self.user_unlike(user=user)
        self.liked_user_set.add(user)

    def user_dislike(self, user: User) -> None:
        """Dislike this post, for a given user, ensuring it's not liked at the same time."""
        self.user_unlike(user=user)
        self.disliked_user_set.add(user)

    def user_unlike(self, user: User) -> None:
        """Remove like and dislike from this post, for a given user."""
        self.liked_user_set.remove(user)
        self.disliked_user_set.remove(user)

    @property
    def student_type(self) -> str:
        """The formatted type of student that wrote this post."""
        first_course: Course | None = self.module.course_set.filter(
            pk__in=self.user.enrolled_course_set.values_list("pk", flat=True)
        ).first()

        if not first_course:
            raise Course.DoesNotExist

        return first_course.student_type

    def report(self, reporter: User, reason: "Report.Reasons") -> None:
        """Report this post by the given user."""
        Report.objects.create(post=self, reporter=reporter, reason=reason)

    @override
    def __str__(self) -> str:
        return f"Post by a {self.student_type} for {self.module}"


class Report(CustomBaseModel):
    """Model class for reports, that users can make about posts."""

    class Reasons(models.TextChoices):
        """Enum of reason codes & display values of each reason."""

        HATE = "HAT", _("Hate Speech or Language")
        IDENTIFYING_INFO = "IDE", _("Identifying Information")
        ASSIGNMENT_ANSWERS = "ANS", _("Assignment Answers")
        SPAM = "SPM", _("SPAM")
        BULLYING = "BUL", _("Bullying or Harassment")
        FALSE_INFO = "FLS", _("False Information")
        SEXUAL = "SEX", _("Sexual Content")

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="report_set",
        verbose_name=_("Post")
    )
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="made_report_set",
        verbose_name=_("User")
    )
    reason = models.CharField(
        choices=Reasons.choices,
        max_length=3,
        verbose_name=_("Reason")
    )
    solved = models.BooleanField(
        _("Is_Solved"),
        default=False
    )

    class Meta:
        """Metadata options about this model."""

        verbose_name = _("Report")

    @override
    def __str__(self) -> str:
        return f"Report by {self.reporter} for {self.reason} on post {self.post}"
