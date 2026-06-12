from unittest.mock import patch

from sendhub.version import get_version


@patch("pathlib.Path.read_text", return_value='VERSION="1.2.3"')
def test_get_version_accepts_assignment_syntax(mock_read_text):
    assert get_version() == "1.2.3"


@patch("pathlib.Path.read_text", return_value="2.3.4")
def test_get_version_accepts_plain_version(mock_read_text):
    assert get_version() == "2.3.4"


@patch("pathlib.Path.read_text", return_value="not-a-version")
def test_get_version_falls_back_on_malformed_content(mock_read_text):
    assert get_version() == "0.26.01"


@patch("pathlib.Path.read_text", side_effect=OSError("missing"))
def test_get_version_falls_back_on_read_error(mock_read_text):
    assert get_version() == "0.26.01"
