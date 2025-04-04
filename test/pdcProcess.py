import PyPDF2

def read_pdf(file_path):
    """
    Reads the text content of a PDF file.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        str: The extracted text content, or None if an error occurs.
    """
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() or "" #Handle cases where page.extract_text() returns None.
            return text
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except PyPDF2.errors.PdfReadError:
        print(f"Error: Could not read PDF at {file_path}. It might be corrupted or encrypted.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
# Example usage:
pdf_file = "example.pdf" # Replace with your PDF file path
extracted_text = read_pdf(pdf_file)

if extracted_text:
    print(extracted_text)

# Example using a memory stream instead of file path.
import io

def read_pdf_from_memory(pdf_bytes):
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

#example of reading from memory stream
# with open(pdf_file, 'rb') as f:
#     pdf_bytes = f.read()
#     memory_text = read_pdf_from_memory(pdf_bytes)
#     if memory_text:
#         print(memory_text)