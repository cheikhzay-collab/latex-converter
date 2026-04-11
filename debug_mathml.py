from app import get_omml, preprocess_copied_math, add_math_to_run
from docx import Document
import html

doc = Document()
p = doc.add_paragraph()

# Mimic the error path in process_inline
text = "g"
latex = html.unescape(text)

try:
    print(f"Testing get_omml for: {latex}")
    omml_node = get_omml(latex)
    if omml_node is not None:
        print("Success!")
    else:
        print("omml_node is None")
except Exception as e:
    import traceback
    traceback.print_exc()

