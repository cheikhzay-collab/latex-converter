from app import preprocess_copied_math, html_to_docx
import markdown
from docx import Document
import io

text = r"""Voici le texte extrait de l’image :

---

# **Integration Formula**

Here is an example equation:

[
\int_a^b x^2 \, dx = \frac{b^3 - a^3}{3}
]

And an inline one: (E = mc^2).

## **Properties**

* The function is **continuous** on ([a, b])
* The derivative: (f'(x) = 2x)
* A table:

**Variable** | **Value**
a | 0
b | 1

---"""

# 1. Preprocess
clean_text = preprocess_copied_math(text)

# 2. Convert to HTML via Markdown
html_body = markdown.markdown(clean_text, extensions=['extra', 'nl2br'])

# 3. Create Document
doc = Document()

# 4. Map HTML to Docx
html_to_docx(f"<body>{html_body}</body>", doc, is_rtl=False)

# 5. Save
doc.save("test_gpt.docx")
print("Done. Check test_gpt.docx")
