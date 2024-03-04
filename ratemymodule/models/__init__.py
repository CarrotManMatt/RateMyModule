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

import datetime
from collections.abc import Callable, Iterable
from collections.abc import Set as ImmutableSet
from typing import Final, override

import tldextract
from allauth.account.models import EmailAddress
from django.contrib import auth
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.db.models.manager import RelatedManager

from .managers import UniversityModuleManager, UserManager, UserModuleManager
from .utils import AttributeDeleter, CustomBaseModel
from .validators import (
    ConfusableEmailValidator,
    ExampleEmailValidator,
    FreeEmailValidator,
    HTML5EmailValidator,
    UnicodePropertiesRegexValidator,
)

# NOTE: Adding external package functions to the global scope for frequent usage
get_user_model: Callable[[], "User"] = auth.get_user_model  # type: ignore[assignment]

EARLIEST_TEACHING_YEAR: Final[int] = 1096
LATEST_TEACHING_YEAR: Final[int] = 3000


class User(CustomBaseModel, AbstractBaseUser, PermissionsMixin):
    """Primary model class for users that can create an account & log into it."""

    normalize_username = AttributeDeleter(  # type: ignore[assignment]
        object_name="User",
        attribute_name="normalize_username"
    )

    password = models.CharField(
        verbose_name=_("Password"),
        max_length=128,
        error_messages={
            "null": _("Password is a required field."),
            "blank": _("Password is a required field.")
        }
    )
    email = models.EmailField(
        verbose_name=_("Email Address"),
        max_length=255,
        unique=True,
        validators=(
            HTML5EmailValidator(),
            FreeEmailValidator(),
            ConfusableEmailValidator(),
            ExampleEmailValidator()
        ),
        error_messages={
            "unique": _("A user with that Email Address already exists."),
            "max_length": _("The Email Address must be at most 255 digits.")
        }
    )
    is_superuser = models.BooleanField(
        verbose_name=_("Is Superuser?"),
        default=False,
        help_text=_(
            "Designates that this user has all permissions without "
            "explicitly assigning them."
        )
    )
    is_staff = models.BooleanField(
        verbose_name=_("Is Staff?"),
        default=False,
        help_text=_("Designates whether the user can log into the admin site.")
    )
    is_active = models.BooleanField(
        verbose_name=_("Is Active?"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        )
    )
    liked_post_set = models.ManyToManyField(
        "ratemymodule.Post",
        related_name="liked_user_set",
        verbose_name=_("Liked Posts"),
        help_text=_("The set of posts this user has liked."),
        blank=True
    )
    disliked_post_set = models.ManyToManyField(
        "ratemymodule.Post",
        related_name="disliked_user_set",
        verbose_name=_("Disliked Posts"),
        help_text=_("The set of posts this user has disliked."),
        blank=True
    )
    enrolled_course_set = models.ManyToManyField(
        "ratemymodule.Course",
        related_name="enrolled_user_set",
        verbose_name=_("Enrolled Courses"),
        help_text=_("The set of courses this user has enrolled in."),
        blank=True
    )

    objects = UserManager()
    # noinspection SpellCheckingInspection
    emailaddress_set: RelatedManager[EmailAddress]  # type: ignore[no-any-unimported]
    made_post_set: RelatedManager["Post"]
    made_report_set: RelatedManager["Report"]

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"

    @property
    def date_time_joined(self) -> datetime.datetime:
        """Shortcut accessor to the time this `User` object was created."""
        return self.date_time_created

    @date_time_joined.setter
    def date_time_joined(self, __value: datetime.datetime) -> None:
        self.date_time_created = __value

    @property
    def university(self) -> "University | None":
        """
        Shortcut accessor to the university this user is a student at.

        If the user is a staff member, they may have no university.
        """
        return self._get_university_from_email_domain(
            self.email.rpartition("@")[2],
            is_staff=any((self.is_staff, self.is_superuser))
        )

    @staticmethod
    def _get_university_from_email_domain(email_domain: str, *, is_staff: bool) -> "University | None":  # noqa: E501
        try:
            return (
                University.objects.alias(full_email_domain=models.Value(email_domain)).get(
                    full_email_domain__endswith=models.F("email_domain")
                )
            )
        except University.DoesNotExist:
            if is_staff:
                return None

            raise

    class Meta:
        """Metadata options about this model."""

        verbose_name = _("User")
        constraints = (
            models.CheckConstraint(
                name="ensure_superusers_are_staff",
                check=~models.Q(is_superuser=True, is_staff=False)
            ),
        )

    @override
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        self.module_set: UserModuleManager = UserModuleManager(self)

    @override
    def __str__(self) -> str:
        return self.email

    @override
    def save(self, *, force_insert: bool = False, force_update: bool = False, using: str | None = None, update_fields: Iterable[str] | None = None) -> None:  # type: ignore[override]  # noqa: E501
        if self.is_superuser:
            self.is_staff = True

        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )

        self.liked_post_set.add(*self.made_post_set.all())
        self.disliked_post_set.through.objects.filter(post__user=self).delete()  # type: ignore[attr-defined]

    def _validate_email_not_already_exists(self) -> None:
        local: str
        domain: str
        local, __, domain = self.email.rpartition("@")

        EMAIL_ALREADY_EXISTS: Final[bool] = (
            get_user_model().objects.exclude(email=self.email).exclude(pk=self.pk).filter(
                email__icontains=f"{local}@{tldextract.extract(domain).domain}"
            ).exists()
        )
        if EMAIL_ALREADY_EXISTS:
            raise ValidationError(
                {"email": _("That Email Address is already in use by another user.")},
                code="unique"
            )

    @override
    def clean(self) -> None:
        self._validate_email_not_already_exists()

        try:
            __ = self.university
        except University.DoesNotExist:
            raise ValidationError(
                {
                    "email": _(
                        "Your email address must be linked to a university registered account."
                    )
                },
                code="invalid"
            ) from None

    @classmethod
    @override
    def get_proxy_field_names(cls) -> ImmutableSet[str]:
        return super().get_proxy_field_names() | {"date_time_joined"}

    def like_post(self, post: "Post") -> None:
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
        validators=(
            MinLengthValidator(2),
            UnicodePropertiesRegexValidator(r"\A[\p{L}!?¿¡' &()-]+\Z")
        )
    )
    short_name = models.CharField(
        max_length=5,
        unique=False,
        verbose_name=_("Short Name"),
        validators=(
            MinLengthValidator(2),
            UnicodePropertiesRegexValidator(r"\A[\p{L}!?¿¡'-]+\Z")
        )
    )
    email_domain = models.CharField(
        max_length=253,
        unique=True,
        verbose_name=_("Email Domain"),
        validators=(
            MinLengthValidator(4),
            RegexValidator(
                r"\A((?!-))((xn--)?[a-z0-9][a-z0-9-_]{0,61}[a-z0-9]{0,1}\.)+(xn--)?([a-z0-9\-]{1,61}|[a-z0-9-]{1,30}\.[a-z]{2,})\Z"
            )
        )
    )
    founding_date = models.DateField(
        verbose_name=_("Date Founded"),
        help_text=_("Date format DD/MM/YYYY"),
        validators=(
            MinValueValidator(datetime.date(year=EARLIEST_TEACHING_YEAR, month=1, day=1)),
            MaxValueValidator(datetime.date(year=LATEST_TEACHING_YEAR, month=1, day=1))
        )
    )

    course_set: RelatedManager["Course"]

    class Meta:
        """Metadata options about this model."""

        verbose_name = _("University")
        verbose_name_plural = _("Universities")
        constraints = (
            models.CheckConstraint(
                name="ensure_email_domain_adheres_to_regex",
                check=models.Q(
                    email_domain__regex=r"\A((?!-))((xn--)?[a-z0-9][a-z0-9-_]{0,61}[a-z0-9]{0,1}\.)+(xn--)?([a-z0-9\-]{1,61}|[a-z0-9-]{1,30}\.[a-z]{2,})\Z"
                )
            ),
        )

    @override
    def save(self, *, force_insert: bool = False, force_update: bool = False, using: str | None = None, update_fields: Iterable[str] | None = None) -> None:  # type: ignore[override]  # noqa: E501
        self.email_domain = self.email_domain.lower()

        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )

    @override
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        self.module_set: UniversityModuleManager = UniversityModuleManager(self)

    @override
    def __str__(self) -> str:
        return self.name


class Course(CustomBaseModel):
    """Model class for Courses that users can be enrolled in."""

    name = models.CharField(
        max_length=60,
        verbose_name=_("Name"),
        validators=(
            MinLengthValidator(3),
            UnicodePropertiesRegexValidator(r"\A[\p{L}\p{N}!?¿¡' &()-]+\Z")
        )
    )
    student_type = models.CharField(
        max_length=60,
        verbose_name=_("Student Type"),
        validators=(
            MinLengthValidator(3),
            UnicodePropertiesRegexValidator(r"\A[\p{L}!?¿¡' &()-]+\Z")
        )
    )
    university = models.ForeignKey(
        University,
        related_name="course_set",
        verbose_name=_("University"),
        on_delete=models.PROTECT,
        help_text=_("The university that this course is taught at")
    )

    module_set: RelatedManager["Module"]
    enrolled_user_set: RelatedManager["User"]

    class Meta:
        """Metadata options about this model."""

        verbose_name = _("Course")
        constraints = (
            models.UniqueConstraint(
                fields=("name", "university"),
                name="unique_university_course_name"
            ),
        )

    @override
    def __str__(self) -> str:
        return f"{self.name} - {self.university}"


class Module(CustomBaseModel):
    """Model class for modules that can have posts made about them."""

    name = models.CharField(
        max_length=60,
        verbose_name=_("Name"),
        validators=(
            MinLengthValidator(3),
            UnicodePropertiesRegexValidator(r"\A[\p{L}\p{N}!?¿¡' &()-]+\Z")
        )
    )
    code = models.CharField(
        max_length=60,
        verbose_name=_("Reference Code"),
        help_text=_("The unique reference code of this module within its university"),
        validators=(
            MinLengthValidator(2),
            UnicodePropertiesRegexValidator(r"\A[\p{L}0-9!?¿¡' &()-]+\Z")
        )
    )
    year_started = models.DateField(
        verbose_name=_("Year Started"),
        help_text=_("Date format DD/MM/YYYY"),
        validators=(
            MinValueValidator(datetime.date(year=EARLIEST_TEACHING_YEAR, month=1, day=1)),
            MaxValueValidator(datetime.date(year=LATEST_TEACHING_YEAR, month=1, day=1))
        )
    )
    course_set = models.ManyToManyField(
        Course,
        related_name="module_set",
        verbose_name=_("Attached Courses"),
        help_text=_("The set of courses that can include this module"),
        blank=False
    )

    class Meta:
        """Metadata options about this model."""

        verbose_name = _("Module")

    @override
    def clean(self) -> None:
        if self.pk:  # noqa: SIM102
            if self.course_set.exclude(university=self.university).exists():
                raise ValidationError(
                    _("A module cannot be linked to courses across multiple universities."),
                    code="invalid"
                )

    @property
    def university(self) -> University:
        """Shortcut accessor to the university this module belongs to."""
        first_enrolled_course: Course | None = self.course_set.first()
        if not first_enrolled_course:
            raise Course.DoesNotExist

        return first_enrolled_course.university

    # noinspection PyOverrides
    @override  # type: ignore[misc]
    def get_absolute_url(self) -> str:
        """Return the canonical URL for a given `Module` object instance."""
        # TODO: Implement function to get absolute URL
        raise NotImplementedError

    @override
    def __str__(self) -> str:
        return f"{self.name} - {self.university}"


class BaseTag(CustomBaseModel):
    """Base model class for tags that can be added to posts."""

    name = models.CharField(
        max_length=60,
        unique=True,
        verbose_name=_("Tag Name"),
        validators=(
            MinLengthValidator(2),
            UnicodePropertiesRegexValidator(r"\A[\p{L}!?¿¡' &()-]+\Z")
        )
    )
    is_verified = models.BooleanField(default=False, verbose_name=_("Is Verified?"))

    post_set: RelatedManager["Post"]

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

    @override
    def clean(self) -> None:
        TAG_NAME_EXISTS: Final[bool] = (
            OtherTag.objects.filter(name__iexact=self.name.casefold()).exists()
            or ToolTag.objects.filter(name__iexact=self.name.casefold()).exists()
            or (
                TopicTag.objects.exclude(pk=self.pk).filter(
                    name__iexact=self.name.casefold()
                ).exists()
            )
        )
        if TAG_NAME_EXISTS:
            raise ValidationError(
                {"name": _("A tag with this name already exists.")},
                code="unique"
            )


class OtherTag(BaseTag):
    """Model class for other tags describing a module, that can be added to posts."""

    class Meta:
        """Metadata options about this model."""

        verbose_name = _("Other Tag")

    @override
    def clean(self) -> None:
        TAG_NAME_EXISTS: Final[bool] = (
            TopicTag.objects.filter(name__iexact=self.name.casefold()).exists()
            or ToolTag.objects.filter(name__iexact=self.name.casefold()).exists()
            or (
                OtherTag.objects.exclude(pk=self.pk).filter(
                    name__iexact=self.name.casefold()
                ).exists()
            )
        )
        if TAG_NAME_EXISTS:
            raise ValidationError(
                {"name": _("A tag with this name already exists.")},
                code="unique"
            )


class ToolTag(BaseTag):
    """Model class for tags about the tools used in a module, that can be added to posts."""

    class Meta:
        """Metadata options about this model."""

        verbose_name = _("Tool Tag")

    @override
    def clean(self) -> None:
        TAG_NAME_EXISTS: Final[bool] = (
            OtherTag.objects.filter(name__iexact=self.name.casefold()).exists()
            or TopicTag.objects.filter(name__iexact=self.name.casefold()).exists()
            or (
                ToolTag.objects.exclude(pk=self.pk).filter(
                    name__iexact=self.name.casefold()
                ).exists()
            )
        )
        if TAG_NAME_EXISTS:
            raise ValidationError(
                {"name": _("A tag with this name already exists.")},
                code="unique"
            )


# NOTE: Choices classes need to be defined outside of their respective models, so that they can be referenced within the model's Meta constraints list
class _Ratings(models.IntegerChoices):
    """Enum of post star rating numbers."""

    ONE = 1, "1"
    TWO = 2, "2"
    THREE = 3, "3"
    FOUR = 4, "4"
    FIVE = 5, "5"


class Post(CustomBaseModel):
    """Core model class for posts that can be made by users about modules."""

    Ratings: type[_Ratings] = _Ratings

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

    overall_rating = models.PositiveSmallIntegerField(
        choices=Ratings.choices,
        verbose_name=_("Overall Rating")
    )
    difficulty_rating = models.PositiveSmallIntegerField(
        choices=Ratings.choices,
        null=True,
        blank=True,
        verbose_name=_("Difficulty Rating")
    )
    assessment_rating = models.PositiveSmallIntegerField(
        choices=Ratings.choices,
        null=True,
        blank=True,
        verbose_name=_("Assessment Rating")
    )
    teaching_rating = models.PositiveSmallIntegerField(
        choices=Ratings.choices,
        null=True,
        blank=True,
        verbose_name=_("Teaching Rating")
    )
    content = models.TextField(
        verbose_name=_("Content"),
        null=False,
        blank=True,
        validators=(RegexValidator(r"\A\Z|\A.{3,}\Z"),)
    )
    academic_year_start = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(EARLIEST_TEACHING_YEAR),
            MaxValueValidator(LATEST_TEACHING_YEAR)
        ),
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
        constraints = (
            models.UniqueConstraint(
                fields=("user", "module"),
                name="unique_post_creator_with_module"
            ),
            *(
                models.CheckConstraint(
                    name=f"ensure_{rating_field}_valid_choice",
                    check=models.Q(**{f"{rating_field}__in": _Ratings.values})
                )
                for rating_field
                in (
                    "overall_rating",
                    "difficulty_rating",
                    "assessment_rating",
                    "teaching_rating"
                )
            )
        )

    @override
    def save(self, *, force_insert: bool = False, force_update: bool = False, using: str | None = None, update_fields: Iterable[str] | None = None) -> None:  # type: ignore[override]  # noqa: E501
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )

        if self.user not in self.liked_user_set.all():
            self.liked_user_set.add(self.user)

        if self.user in self.disliked_user_set.all():
            self.disliked_user_set.remove(self.user)

    @override
    def clean(self) -> None:
        try:
            module: Module = self.module
        except Module.DoesNotExist:
            pass
        else:
            if module not in self.user.module_set.all():
                raise ValidationError(
                    {
                        "module": _(
                            "You cannot create posts about modules that you have not taken."
                        )
                    },
                    code="invalid"
                )

    @classmethod
    @override
    def get_proxy_field_names(cls) -> ImmutableSet[str]:
        return super().get_proxy_field_names() | {"date_time_posted"}

    @property
    def date_time_posted(self) -> datetime.datetime:
        """Shortcut accessor to the time this `Post` object was created."""
        return self.date_time_created

    @date_time_posted.setter
    def date_time_posted(self, __value: datetime.datetime) -> None:
        self.date_time_created = __value

    @property
    def likes_count(self) -> int:
        """The number of likes this post has."""
        return self.liked_user_set.count()

    @property
    def dislikes_count(self) -> int:
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
            if self.user.is_staff:
                return "an administrator"

            raise Course.DoesNotExist

        return first_course.student_type

    def report(self, reporter: User, reason: "_Reasons") -> None:
        """Report this post by the given user."""
        Report.objects.create(post=self, reporter=reporter, reason=reason)

    @override
    def __str__(self) -> str:
        return f"Post by {self.student_type} for {self.module}"


# NOTE: Choices classes need to be defined outside of their respective models, so that they can be referenced within the model's Meta constraints list
class _Reasons(models.TextChoices):
    """Enum of report reason codes & display values of each reason."""

    HATE = "HAT", _("Hate Speech or Language")
    IDENTIFYING_INFO = "IDE", _("Identifying Information")
    ASSIGNMENT_ANSWERS = "ANS", _("Assignment Answers")
    SPAM = "SPM", _("SPAM")
    BULLYING = "BUL", _("Bullying or Harassment")
    FALSE_INFO = "FLS", _("False Information")
    SEXUAL = "SEX", _("Sexual Content")


class Report(CustomBaseModel):
    """Model class for reports, that users can make about posts."""

    Reasons: type[_Reasons] = _Reasons

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
        verbose_name=_("Reporter")
    )
    reason = models.CharField(
        choices=Reasons.choices,
        max_length=3,
        verbose_name=_("Reason")
    )
    is_solved = models.BooleanField(
        _("Is_Solved"),
        default=False
    )

    class Meta:
        """Metadata options about this model."""

        verbose_name = _("Report")
        constraints = (
            models.CheckConstraint(
                name="ensure_reason_valid_choice",
                check=models.Q(reason__in=_Reasons.values)
            ),
        )

    @override
    def clean(self) -> None:
        if self.reporter == self.post.user:
            raise ValidationError(
                {"post": _("You cannot report your own posts.")},
                code="invalid"
            )

    @override
    def __str__(self) -> str:
        return f"Report by {self.reporter} for {self.reason} on post {self.post}"
