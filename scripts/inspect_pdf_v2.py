import re
from pypdf import PdfReader

def inspect_pages(pdf_path, start_page=20, num_pages=5):
    reader = PdfReader(pdf_path)
    for i in range(start_page, start_page + num_pages):
        page = reader.pages[i]
        text = page.extract_text()
        print(f"\n--- Page {i + 1} ---\n{text}\n")

if __name__ == "__main__":
    inspect_pages("Directory_of_Indian_Museums_080620231.pdf")
