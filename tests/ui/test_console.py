from src.ui.console import NoxValidator, NoxConsole
from unittest.mock import patch, Mock, ANY
import pytest
from questionary import Style


# Tests for NoxValidator
@pytest.mark.parametrize("text, expected_result", [
    ("123", True),
    ("0", True),
    ("abc", "The answer can only be an integer."),
    ("", "The answer can only be an integer."),
    ("1.23", "The answer can only be an integer."),
    ("-10", "The answer can only be an integer."), # .isdigit() does not handle negative numbers
])
def test_is_integer_validator(text, expected_result):
    # Arrange
    validator = NoxValidator.is_integer()

    # Act
    result = validator(text)

    # Assert
    assert result == expected_result


@pytest.mark.parametrize("text, expected_result", [
    (" a ", True),
    ("something", True),
    ("  ", "The answer can't be empty."),
    ("\t", "The answer can't be empty."),
    ("", "The answer can't be empty."),
])
def test_is_not_empty_validator(text, expected_result):
    # Arrange
    validator = NoxValidator.is_not_empty()

    # Act
    result = validator(text)

    # Assert
    assert result == expected_result


# Tests for NoxConsole
def test_ask_integer_handles_none_on_skip():
    # Arrange
    console = NoxConsole()
    # Mock the underlying questionary call to simulate a user skipping (e.g., Ctrl+C or skip=True)
    with patch('questionary.text') as mock_questionary_text:
        mock_questionary_text.return_value.skip_if.return_value.ask.return_value = None

        # Act
        result = console.ask_integer("Enter a number", skip=True)

        # Assert
        assert result is None
        mock_questionary_text.assert_called_once()


def test_ask_text_returns_expected_value():
    # Arrange
    console = NoxConsole()
    expected_input = "user_input_text"
    with patch('questionary.text') as mock_questionary_text, \
         patch('src.ui.console.NoxValidator.is_not_empty') as mock_validator: # Patch the validator function
        # Ensure the patched validator returns a mock callable
        mock_validator.return_value = Mock(name="is_not_empty_validator")

        mock_questionary_text.return_value.skip_if.return_value.ask.return_value = expected_input

        # Act
        result = console.ask_text("Enter text")

        # Assert
        assert result == expected_input
        mock_questionary_text.assert_called_once_with(
            message="Enter text",
            validate=mock_validator.return_value, # Assert that our mock validator was passed
            style=console.style
        )
        mock_validator.assert_called_once() # Assert that the validator was called to get the callable


def test_ask_select_returns_expected_value():
    # Arrange
    console = NoxConsole()
    choices = ["Option1", "Option2"]
    expected_selection = "Option1"
    with patch('questionary.select') as mock_questionary_select:
        mock_questionary_select.return_value.skip_if.return_value.ask.return_value = expected_selection

        # Act
        result = console.ask_select("Select an option", choices)

        # Assert
        assert result == expected_selection
        mock_questionary_select.assert_called_once_with(
            message="Select an option",
            choices=choices,
            style=console.style
        )


def test_ask_autocomplete_returns_expected_value():
    # Arrange
    console = NoxConsole()
    choices = ["Apple", "Banana", "Cherry"]
    expected_selection = "Banana"
    with patch('questionary.autocomplete') as mock_questionary_autocomplete, \
         patch('src.ui.console.NoxValidator.is_in_choices') as mock_validator: # Patch the validator function
        mock_validator.return_value = Mock(name="is_in_choices_validator")
        mock_questionary_autocomplete.return_value.skip_if.return_value.ask.return_value = expected_selection

        # Act
        result = console.ask_autocomplete("Select fruit", choices)

        # Assert
        assert result == expected_selection
        mock_questionary_autocomplete.assert_called_once_with(
            message="Select fruit",
            choices=choices,
            validate=mock_validator.return_value, # Assert that our mock validator was passed
            style=console.style,
            ignore_case=True
        )
        mock_validator.assert_called_once_with(choices) # Assert that the validator was called with correct choices


def test_ask_confirm_returns_expected_value():
    # Arrange
    console = NoxConsole()
    expected_confirmation = True
    with patch('questionary.confirm') as mock_questionary_confirm:
        mock_questionary_confirm.return_value.skip_if.return_value.ask.return_value = expected_confirmation

        # Act
        result = console.ask_confirm("Confirm action")

        # Assert
        assert result == expected_confirmation
        mock_questionary_confirm.assert_called_once_with(
            message="Confirm action",
            style=console.style
        )


def test_ask_integer_returns_int_value():
    # Arrange
    console = NoxConsole()
    expected_int_input = "123"
    with patch('questionary.text') as mock_questionary_text, \
         patch('src.ui.console.NoxValidator.is_integer') as mock_validator: # Patch the validator function
        mock_validator.return_value = Mock(name="is_integer_validator")
        mock_questionary_text.return_value.skip_if.return_value.ask.return_value = expected_int_input

        # Act
        result = console.ask_integer("Enter an integer")

        # Assert
        assert result == int(expected_int_input)
        assert isinstance(result, int)
        mock_questionary_text.assert_called_once_with(
            message="Enter an integer",
            validate=mock_validator.return_value, # Assert that our mock validator was passed
            style=console.style
        )
        mock_validator.assert_called_once() # Assert that the validator was called to get the callable