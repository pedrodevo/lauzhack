from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def text_to_pdf(text_file, output_path):
    """Creates a PDF file from a text file."""
    pdf_filename = output_path

    # Read the content of the text file
    with open(text_file, 'r') as file:
        lines = file.readlines()

    # Create a PDF
    pdf_canvas = canvas.Canvas(pdf_filename, pagesize=letter)
    y_coordinate = 700  # Initial Y-coordinate for text

    for line in lines:
        pdf_canvas.drawString(100, y_coordinate, line.strip())  # Adjust coordinates as needed
        y_coordinate -= 15  # Space between lines, adjust as needed

    pdf_canvas.save()

    return pdf_filename
