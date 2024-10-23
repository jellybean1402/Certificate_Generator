import math
import streamlit as st
from pdfminer.high_level import extract_text
import fitz  # PyMuPDF
import tempfile
import os
from io import BytesIO

# Define the functions as per your existing code
def extract_and_replace_text(input_pdf, replacements):
    text = extract_text(input_pdf)
    for old_text, new_text in replacements.items():
        text = text.replace(old_text, new_text)
    return text

def split_text_into_paragraphs(text):
    return text.split('\n\n')

def calculate_text_width(fontsize, text):
    temp_pdf = fitz.open()
    temp_page = temp_pdf.new_page()
    temp_page.insert_text((0, 0), text, fontsize=fontsize, render_mode=0)
    text_bbox = temp_page.get_text("dict")['blocks'][0]['lines'][0]['spans'][0]['bbox']
    text_width = text_bbox[2] - text_bbox[0]
    temp_pdf.close()
    return text_width

def wrap_paragraph(paragraph, max_char_limit=75):
    words = paragraph.split()  # Split the paragraph into words
    lines = []
    current_line = []

    for word in words:
        # Check if adding the next word would exceed the max_char_limit
        if len(' '.join(current_line + [word])) <= max_char_limit:
            current_line.append(word)
        else:
            # If it exceeds, join the current line into a string and add it to lines
            lines.append(' '.join(current_line))
            # Start a new line with the current word
            current_line = [word]

    # Add the last line if there are any words left
    if current_line:
        lines.append(' '.join(current_line))

    return '\n'.join(lines)  # Join the lines with newlines for each line

def add_text_box_to_pdf(pdf_path, text_entries, positions, font_sizes, colors, paragraphs_list):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(0)
    page_width = page.rect.width

    for i, (text, position, fontsize, color) in enumerate(zip(text_entries, positions, font_sizes, colors)):
        if text == paragraphs_list[1]:
            x = (page_width - len(text) * 23) / 2
            y = position
        else:
            x, y = position
        text = wrap_paragraph(text)
        page.insert_text((x, y), text, fontsize=fontsize, color=color, render_mode=0)


    output_pdf = BytesIO()
    pdf_document.save(output_pdf)
    pdf_document.close()

    output_pdf.seek(0)

    return output_pdf

# Streamlit application
def main():
    st.title('Akshar Pauul Certificate Generator')

    st.sidebar.header('Input Parameters')
    name = st.sidebar.text_input('Name', placeholder='Enter Name')
    hours = st.sidebar.text_input('Hours', placeholder='Enter the number of hours')
    work = st.sidebar.text_input('Work', placeholder='Enter the work done')
    date = st.sidebar.text_input('Date', placeholder='dd/mm/yyyy')

    if st.button('Process PDF'):
        st.write("Processing...")

        input_pdf = 'input.pdf'  # The existing PDF file
        replacements = {
            '<<name>>': name,
            '<<hours>>': hours + " hours",
            '<<work>>': work,
            '<<date>>': date
        }

        # Extract and replace text
        modified_text = extract_and_replace_text(input_pdf, replacements)


        paragraphs_list = split_text_into_paragraphs(modified_text)

        # Define file paths and text properties
        background_pdf = 'background.pdf'

        # Define your texts, positions, font sizes, and colors
        text_entries = [paragraphs_list[i] for i in range(min(6, len(paragraphs_list)))]
        positions = [(815, 285), 665, (100, 750), (100, 970), (80, 1400), (430, 1450)]
        font_sizes = [14, 40, 25, 25, 25, 20]
        colors = [(0.25, 0.25, 0.25), (0.2, 0.2, 0.2), (0, 0, 0), (0, 0, 0), (0.25, 0.25, 0.25), (0.25, 0.25, 0.25)]

        processed_pdf = add_text_box_to_pdf(background_pdf, text_entries, positions, font_sizes, colors, paragraphs_list)


        st.success("PDF processing complete!")

        name_of_output_file = f"{name}-{work}.pdf"

        st.download_button(label="Download Processed PDF", data=processed_pdf, file_name=name_of_output_file, mime="application/pdf")


if __name__ == "__main__":
    main()
