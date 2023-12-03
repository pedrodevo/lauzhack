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

def create_exam_pdf(questions, output_filename):
    # Create a canvas (PDF document)
    c = canvas.Canvas(output_filename, pagesize=letter)
    
    # Set font and size for the exam
    c.setFont("Helvetica", 12)
    
    # Add title for the exam
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 750, "Exam Sample")
    
    # Set font back to normal for questions
    c.setFont("Helvetica", 12)
    
    # Add questions to the PDF
    question_start_y = 720  # Starting y-coordinate for the questions
    question_spacing = 20    # Space between questions
    
    for idx, question in enumerate(questions, start=1):
        if idx % 5 == 0:
            c.showPage()  # Start a new page after every 5 questions
        
        question_y = question_start_y - (idx % 5) * question_spacing
        c.drawString(100, question_y, f"Question {idx}: {question}")
    
    c.save()

# Example list of questions
questions_list = [
    "What is the capital of France?",
    "Who painted the Mona Lisa?",
    "What is the powerhouse of the cell?"
]

# Replace 'questions_list' with your own list of questions
create_exam_pdf(questions_list, "exam.pdf")

