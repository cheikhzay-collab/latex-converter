from docx import Document

doc = Document("test_chatgpt_complex.docx")
with open("docx_output.txt", "w", encoding="utf-8") as f:
    for i, p in enumerate(doc.paragraphs):
        f.write(f"Para {i}:\n")
        for r in p.runs:
            f.write(f"  Run: {r.text}\n")
        f.write(f"  XML: {p._element.xml}\n")
