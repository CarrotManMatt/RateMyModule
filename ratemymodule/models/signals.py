"""Handles signals sent within the `ratemymodule` app."""

from collections.abc import Sequence

__all__: Sequence[str] = ("ready",)


def ready() -> None:
    """Initialise this module when importing & starting signal listeners."""

# TODO: Signal to prevent deleting all courses from user (if they are not staff)
# TODO: Signal to prevent deleting user from course if it would make their enrolled_course_set empty (if they are not staff)
# TODO: Signal to prevent deleting module from course if it would make module's course_set empty
# TODO: Signal to prevent deleting all courses from module
# TODO: Signal to ensure course added to user's enrolled_course_set are at same university
# TODO: Signal to ensure course added to module's course_set are at same university
# TODO: Signal to ensure user added to course's enrolled_user_set are at same university
# TODO: Signal to ensure module added to course's module_set are at same university
# TODO: Signal to ensure module added to course's module_set does not have same name as any other module in course's university
# TODO: Signal to ensure module added to course's module_set does not have same code as any other module in course's university
# TODO: Signal to ensure course added to module's course_set does not have a module at it's university with the same name
# TODO: Signal to ensure course added to module's course_set does not have a module at it's university with the same code
# TODO: Signal to prevent removing course from module or from user if there is a post forcing a link
# TODO: Signal to prevent removing module or user from course if there is a post forcing a link
# TODO: Signal to remove post dislike when added to a user's liked_post_set
# TODO: Signal to remove post like when added to a user's disliked_post_set
# TODO: Signal to remove user from disliked_user_set when added to post's liked_user_set
# TODO: Signal to remove user from liked_user_set when added to post's disliked_user_set
# TODO: Signal to prevent removing post from creator's liked_post_set
# TODO: Signal to prevent removing creator from post's liked_user_set
# TODO: Signal to prevent adding post creator to creator's disliked_post_set
# TODO: Signal to prevent adding creator to post's disliked_user_set
# TODO: Signal to ensure course added to user's enrolled_course_set has course's university's email_domain matching user's email domain
# TODO: Signal to ensure user added to course's enrolled_user_set has user's email domain matching course's university's email_domain
