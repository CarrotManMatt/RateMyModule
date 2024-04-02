"""Custom exceptions used throughout this project for specific error handling."""

from collections.abc import Sequence

__all__: Sequence[str] = ("NotEnoughTestDataError",)

from typing import override


class NotEnoughTestDataError(StopIteration):
    """
    Not enough test data values were available to generate a value for the given field.

    Test data is retrieved from the test data JSON file.
    """

    DEFAULT_MESSAGE: str = (
        "Not enough test data values were available, "
        "to generate one from the test data JSON file."
    )

    @override
    def __init__(self, message: str | None = None, model_name: str | None = None, field_name: str | None = None) -> None:  # noqa: E501
        self.message: str = message or self.DEFAULT_MESSAGE
        self.model_name: str | None = model_name
        self.field_name: str | None = field_name

        super().__init__(message or self.DEFAULT_MESSAGE)

    @override
    def __str__(self) -> str:
        """Return the formatted message & properties of the NotEnoughTestDataError."""
        return (
            f"{self.message} (model_name={self.model_name!r}, field_name={self.field_name!r})"
        )
