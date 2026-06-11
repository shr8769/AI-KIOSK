from markdown_pdf import MarkdownPdf, Section
import sys

def main():
    try:
        pdf = MarkdownPdf(toc_level=2)
        # We replace the local image link with an absolute file path or just run it in the same dir
        pdf.add_section(Section(open("requirements_document.md", "r", encoding="utf-8").read()))
        pdf.save("requirements_document.pdf")
        print("Successfully generated requirements_document.pdf")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
