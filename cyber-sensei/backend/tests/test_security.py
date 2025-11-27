import pytest
from unittest.mock import MagicMock, patch
from app.tasks import extract_text_from_document

@patch("app.tasks.magic")
@patch("app.tasks.os.path.exists")
def test_malicious_file_upload(mock_exists, mock_magic):
    """Test that a file with incorrect MIME type is rejected."""
    mock_exists.return_value = True
    
    # Mock magic to return an executable MIME type
    mock_mime = MagicMock()
    mock_mime.from_file.return_value = "application/x-dosexec"
    mock_magic.Magic.return_value = mock_mime
    
    with pytest.raises(ValueError, match="Invalid file type"):
        extract_text_from_document("malicious.pdf")

@patch("app.tasks.magic")
@patch("app.tasks.os.path.exists")
@patch("app.tasks.pypdf")
def test_valid_pdf_upload(mock_pypdf, mock_exists, mock_magic):
    """Test that a valid PDF is accepted."""
    mock_exists.return_value = True
    
    # Mock magic to return PDF MIME type
    mock_mime = MagicMock()
    mock_mime.from_file.return_value = "application/pdf"
    mock_magic.Magic.return_value = mock_mime
    
    # Mock pypdf
    mock_reader = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Sample text"
    mock_reader.pages = [mock_page]
    mock_pypdf.PdfReader.return_value = mock_reader
    
    result = extract_text_from_document("safe.pdf")
    assert result["status"] == "success"
