from app import preprocess_copied_math, html_to_docx
import markdown
from docx import Document

text = r"""
Soit \(g\) la fonction numérique définie sur \(\mathbb{R}\) par :
\[g(x) = \sqrt{x^2 + 3} - x\]
1. Calculer \(\lim_{x \to -\infty} g(x)\).
2. Calculer \(\lim_{x \to +\infty} g(x)\).
3. Montrer que pour tout \(x \in [1, +\infty[\) :
\[0 < g(x) \le \frac{3}{2x}\]
"""

# 1. Preprocess
clean_text = preprocess_copied_math(text)

# 2. Convert to HTML via Markdown
html_body = markdown.markdown(clean_text, extensions=['extra', 'nl2br'])
print("HTML BODY:", html_body)

# 3. Create Document
doc = Document()
html_to_docx(f"<body>{html_body}</body>", doc, is_rtl=False)
doc.save("test_chatgpt_complex.docx")

print("Done")
