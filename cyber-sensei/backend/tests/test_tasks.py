import os
import pytest
from unittest.mock import patch, MagicMock
from app.tasks import extract_text_from_document, process_code_file

# Mock data
SAMPLE_TXT = "Hello World"
SAMPLE_CODE = "def hello():\n    print('Hello')"

@pytest.fixture
def txt_file(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text(SAMPLE_TXT, encoding="utf-8")
    return str(p)

@pytest.fixture
def py_file(tmp_path):
    p = tmp_path / "test.py"
    p.write_text(SAMPLE_CODE, encoding="utf-8")
    return str(p)

def test_extract_text_txt(txt_file):
    result = extract_text_from_document(txt_file)
    assert result["status"] == "success"
    assert result["text_preview"] == SAMPLE_TXT
    assert result["word_count"] == 2

def test_process_code_file(py_file):
    result = process_code_file(py_file)
    assert result["status"] == "success"
    assert result["language"] == "py"
    assert result["lines_of_code"] == 2
    assert result["complexity_score"] > 0

@patch("app.tasks.os.path.exists")
def test_file_not_found(mock_exists):
    mock_exists.return_value = False
    with pytest.raises(FileNotFoundError):
        extract_text_from_document("nonexistent.txt")
