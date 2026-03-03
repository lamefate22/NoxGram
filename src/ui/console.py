from typing import List, Optional, Callable
from questionary import Style
from pathlib import Path
import questionary

DEFAULT_STYLE = Style([
    ('qmark', 'fg:#61afef'),  # Question Mark
    ('question', 'fg:#c5c8c6'),  # Question Text
    ('answer', 'fg:#a0ce51'),  # Answers
    ('pointer', 'fg:#61afef'),  # Pointer for selected item
    ('highlighted', 'fg:#61afef'),  # Highlighted choice
    ('selected', 'fg:#a0ce51'),  # Selected checkbox/list item
    ('text', 'fg:#c5c8c6'),  # Default text (e.g., input)
    ('disabled', 'fg:#808080 italic'),  # Disabled choices
])


class NoxValidator:
    """Static input validation class."""
    @staticmethod
    def is_integer(validation_message: str = "The answer can only be an integer.") -> Callable:
        return lambda text: text.isdigit() or validation_message

    @staticmethod
    def is_not_empty(validation_message: str = "The answer can't be empty.") -> Callable:
        return lambda text: text.strip() != "" or validation_message

    @staticmethod
    def is_in_choices(choices: List[str], validation_message: str = "Invalid choice.") -> Callable:
        return lambda text: text.strip() in choices or validation_message

    @staticmethod
    def is_path_exists(validation_message: str = "Path does not exist.") -> Callable:
        return lambda text: Path(text).exists() or validation_message


class NoxConsole:
    """The class of interaction with the user through the terminal."""
    def __init__(self, style: Style = DEFAULT_STYLE):
        self.style = style

    def ask_text(self, hint: str, skip: bool = False) -> Optional[str]:
        """
        Ask the user to input the text.

        :param hint: the text to ask.
        :param skip: whether to skip the asking or not.
        """
        return questionary.text(
            message=hint,
            validate=NoxValidator.is_not_empty(),
            style=self.style
        ).skip_if(skip, default=None).ask()

    def ask_integer(self, hint: str, skip: bool = False) -> Optional[int]:
        """
        Ask the user to input the integer.
        :param hint: the text to ask.
        :param skip: whether to skip the asking or not.
        """
        response = questionary.text(
            message=hint,
            validate=NoxValidator.is_integer(),
            style=self.style
        ).skip_if(skip, default=None).ask()
        return int(response) if response is not None else None

    def ask_select(self, hint: str, choices: List[str], skip: bool = False) -> Optional[str]:
        """
        Ask the user to select a choice.

        :param hint: the text to ask.
        :param choices: the choices.
        :param skip: whether to skip the asking or not.
        """
        return questionary.select(
            message=hint,
            choices=choices,
            style=self.style
        ).skip_if(skip, default=None).ask()

    def ask_autocomplete(self, hint: str, choices: List[str], skip: bool = False) -> Optional[str]:
        """
        Ask the user to select a choice (autocomplete).

        :param hint: the text to ask.
        :param choices: the choices.
        :param skip: whether to skip the asking or not.
        """
        return questionary.autocomplete(
            message=hint,
            choices=choices,
            validate=NoxValidator.is_in_choices(choices),
            style=self.style,
            ignore_case=True
        ).skip_if(skip, default=None).ask()

    def ask_confirm(self, hint: str, skip: bool = False) -> Optional[bool]:
        """
        Ask the user to confirm the answer.

        :param hint: the text to ask.
        :param skip: whether to skip the asking or not.
        """
        return questionary.confirm(
            message=hint,
            style=self.style
        ).skip_if(skip, default=None).ask()

    def ask_path(self, hint: str, skip: bool = False) -> Optional[Path]:
        """
        Ask the user to select a path.

        :param hint: the text to ask.
        :param skip: whether to skip the asking or not.
        """
        response = questionary.path(
            message=hint,
            validate=NoxValidator.is_path_exists(),
            style=self.style
        ).skip_if(skip, default=None).ask()
        return Path(response) if response else None

    def qprint(self, text: str) -> None:
        """
        Customized print function.

        :param text: the text to print.
        """
        questionary.print(text, style="fg:#c5c8c6")
