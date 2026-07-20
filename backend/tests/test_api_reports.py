import pytest
import io
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_upload_unsupported_format():
    files = {'file': ('test.txt', b'some text', 'text/plain')}
    response = client.post("/api/reports/upload", files=files)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

def test_upload_valid_mock_file():
    mock_pdf_content = b"%PDF-1.4 Mock PDF content for lab report testing"
    files = {'file': ('lab_cbc_report.pdf', io.BytesIO(mock_pdf_content), 'application/pdf')}
    data = {'test_type': 'cbc', 'age': '35', 'sex': 'Male'}
    
    response = client.post("/api/reports/upload", files=files, data=data)
    assert response.status_code == 200
    result = response.json()
    assert result["file_name"] == "lab_cbc_report.pdf"
    assert result["test_type"] == "cbc"
    assert "clinical_explanation" in result
