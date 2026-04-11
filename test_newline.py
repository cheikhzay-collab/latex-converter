import markdown
from app import preprocess_copied_math, html_to_docx
from docx import Document

text = r"""
Here is a chatgpt text with a newline inside inline math:
\(y =
x + 1\)
And display math without newlines:
\[a=b\]
There you go.
"""

clean = preprocess_copied_math(text)
print("--- CLEAN ---")
print(clean)

html = markdown.markdown(clean, extensions=['extra', 'nl2br'])
print("--- HTML ---")
print(html)

doc = Document()
html_to_docx(f"<body>{html}</body>", doc)
doc.save("test_newline.docx")
print("Done")
