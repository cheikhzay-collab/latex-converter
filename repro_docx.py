import io
from app import preprocess_copied_math, get_omml, html_to_docx
from docx import Document
import markdown

# Test Content
content = r"""
# Test Native Docx
This is a test of the new **native** Word export.

## 1. Intervals (Fixed)
Montrer que $x \in [1, +\infty[$.

## 2. Professional Math
Display equation:
$$ \int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2} $$

Inline equation: $E = mc^2$.

## 3. Lists and Tables
- Item A
- Item B

| Column 1 | Column 2 |
|----------|----------|
| Val 1    | Val 2    |
"""

print("--- STARTING DOCX GENERATION TEST ---")

# 1. Preprocess
clean_text = preprocess_copied_math(content)
print("Preprocessing complete.")

# 2. HTML
html_body = markdown.markdown(clean_text, extensions=['extra', 'nl2br'])
full_html = f"<body>{html_body}</body>"
print("Markdown to HTML conversion complete.")

# 3. Docx
doc = Document()
html_to_docx(full_html, doc, is_rtl=False)
print("HTML to Docx mapping complete.")

# 4. Save
doc.save("test_native_output.docx")
print("SUCCESS: test_native_output.docx created.")
