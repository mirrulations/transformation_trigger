import pytest
import boto3
from moto import mock_aws
import os
import sys
from unittest.mock import patch, MagicMock
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json

# Add the parent directory of `app.py` to the Python path
from lambda_functions.pdf_text_extract.app import handler, extract_text  # Import from app.py


def create_sample_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, "Hello, this is a test PDF.")
    c.showPage()
    c.save()
    buffer.seek(0)  # Reset the stream position
    return buffer

# Unit test for extract_text function
def test_extract_text():
    pdf_stream = create_sample_pdf()  # Create a sample PDF file
    extracted_text = extract_text(pdf_stream)  # Extract text from the PDF

    # Ensure the function does not return None or an empty string
    assert extracted_text is not None, "extract_text() returned None"
    assert extracted_text.strip(), "extract_text() returned an empty string"

    # Normalize whitespace and check if expected text is present
    extracted_text = " ".join(extracted_text.split())  # Removes excess whitespace
    expected_text = "Hello, this is a test PDF."

    assert expected_text in extracted_text, f"Unexpected text extracted: '{extracted_text}'"

    # Print extracted text for debugging
    print(f"Extracted text: {extracted_text}")

    print("✅ extract_text function works correctly!")

# Helper function to create a PDF with given text content
def create_pdf_with_text(text_list):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    for index, text in enumerate(text_list):
        c.drawString(100, 750 - (index * 20), text)  # Offset text for readability
        if index % 30 == 29:  # Create a new page every 30 lines
            c.showPage()

    c.showPage()
    c.save()
    buffer.seek(0)  # Reset the stream position
    return buffer

# Test for extracting text from a multi-page PDF
def test_extract_text_multi_page():
    pdf_stream = create_pdf_with_text(["Page 1 content", "Page 2 content", "Page 3 content"])
    extracted_text = extract_text(pdf_stream)

    assert extracted_text is not None and extracted_text.strip(), "extract_text() returned empty text"
    assert "Page 1 content" in extracted_text, "Missing expected text from Page 1"
    assert "Page 2 content" in extracted_text, "Missing expected text from Page 2"
    assert "Page 3 content" in extracted_text, "Missing expected text from Page 3"

    # Print extracted text for debugging
    print(f"Extracted text (multi-page): {extracted_text}")

    print("✅ Multi-page PDF extraction works correctly!")

# Test for extracting text from a PDF with empty pages
def test_extract_text_empty_pages():
    pdf_stream = create_pdf_with_text(["", "", ""])  # Empty pages
    extracted_text = extract_text(pdf_stream)

    assert extracted_text.strip() == "", f"Expected empty text, but got: {extracted_text}"

    # Print extracted text for debugging
    print(f"Extracted text (empty pages): {extracted_text}")

    print("✅ PDF with empty pages processed correctly!")

# Test for extracting text from a PDF with numbers and special characters
def test_extract_text_numbers_and_special_chars():
    pdf_stream = create_pdf_with_text(["1234567890", "!@#$%^&*()_+"])
    extracted_text = extract_text(pdf_stream)

    assert "1234567890" in extracted_text, "Missing numbers in extracted text"
    assert "!@#$%^&*()_+" in extracted_text, "Missing special characters in extracted text"

    # Print extracted text for debugging
    print(f"Extracted text (numbers & special chars): {extracted_text}")

    print("✅ PDF with numbers and special characters processed correctly!")