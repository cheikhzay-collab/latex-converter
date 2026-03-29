from flask import Flask, render_template, request, send_file
from docx import Document
from docx.oxml import OxmlElement
import latex2mathml.converter
import io
import re
import markdown

app = Flask(__name__)

def preprocess_copied_math(text):
    # 1. Math formulas inside brackets: [ f(x) = 3 ] -> $$ f(x) = 3 $$. MUST be on their own line to avoid breaking intervals like [1, +\infty[
    text = re.sub(r'(?m)^[ \t]*\[([^\[\]]*?[=<>+\-*\^][^\[\]]*?)\][ \t]*$', r'$$\1$$', text)
    # 2. Double parentheses: ((C_f)) -> \(C_f\)
    text = re.sub(r'\(\((.*?)\)\)', r'\(\1\)', text)
    # 3. Single function letter or variable: (f) -> \(f\)
    text = re.sub(r'\(([A-Za-z])\)', r'\(\1\)', text)
    # 4. Simple equations in parentheses: (f(x)=3)
    text = re.sub(r'\(([A-Za-z]\([A-Za-z]\)[^()]*?)\)', r'\(\1\)', text)
    return text

def process_text_to_html(text, is_rtl=False):
    text = preprocess_copied_math(text)
    
    # 1. Pre-processing: Identify LaTeX blocks and protect them from Markdown conversion
    # We replace math blocks with placeholders to prevent Markdown from messing them up (e.g., * in formulas)
    
    placeholders = {}
    
    # regex:
    # $$...$$ : matches across lines ([\s\S])
    # \[...\] : matches across lines ([\s\S])
    # $...$   : NO newlines allowed (strict inline)
    # \(...\) : matches across lines ([\s\S]) - Critical for Gemini headers/multiline inline
    pattern = re.compile(r'(\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\$[^\$\n]+\$|\\\([\s\S]*?\\\))')
    
    def replace_math(match):
        # Use a safe token without underscores or special markdown chars
        key = f"MATHBLOCK{len(placeholders)}END"
        placeholders[key] = match.group(1)
        return key
    
    text_with_placeholders = pattern.sub(replace_math, text)
    
    # 2. Convert Markdown to HTML
    # Enable extensions for better formatting (tables, fenced_code)
    html_body = markdown.markdown(text_with_placeholders, extensions=['extra', 'nl2br'])
    
    # 3. Post-processing: Restore math blocks and convert to MathML
    for key, latex_raw in placeholders.items():
        # Strip delimiters
        math_content = ""
        is_display = False
        
        if latex_raw.startswith('$$') and latex_raw.endswith('$$'):
            math_content = latex_raw[2:-2]
            is_display = True
        elif latex_raw.startswith('\\[') and latex_raw.endswith('\\]'):
            math_content = latex_raw[2:-2]
            is_display = True
        elif latex_raw.startswith('$') and latex_raw.endswith('$'):
            math_content = latex_raw[1:-1]
        elif latex_raw.startswith('\\(') and latex_raw.endswith('\\)'):
            math_content = latex_raw[2:-2]
            
        try:
             # Basic cleanup: if content is empty or just whitespace, skip
            if not math_content.strip():
                replacement = latex_raw
            else:
                # IMPORTANT: Replace newlines with spaces. 
                # latex2mathml/LaTeX sometimes chokes on random newlines
                clean_math = math_content.replace('\n', ' ')
                
                mathml = latex2mathml.converter.convert(clean_math)
                if is_display:
                    replacement = f'<p align="center">{mathml}</p>'
                else:
                    replacement = mathml
        except Exception as e:
            # Show the actual error to help user/us debug
            print(f"FAILED: {str(e)}")
            replacement = f'<span style="color:red; font-weight:bold;">[Error: {latex_raw} ({str(e)})]</span>'
            
        html_body = html_body.replace(key, replacement)

    # 4. Construct Full Word-compatible HTML
    # Determine direction and alignment
    body_dir = 'rtl' if is_rtl else 'ltr'
    text_align = 'right' if is_rtl else 'left'
    
    full_html = f"""
    <html xmlns:o='urn:schemas-microsoft-com:office:office' 
          xmlns:w='urn:schemas-microsoft-com:office:word' 
          xmlns:m='http://schemas.microsoft.com/office/2004/12/omml' 
          xmlns='http://www.w3.org/TR/REC-html40'>
    <head>
        <meta charset="utf-8">
        <title>Converted Document</title>
        <!--[if gte mso 9]>
        <xml>
            <w:WordDocument>
                <w:View>Print</w:View>
                <w:Zoom>100</w:Zoom>
                <w:DoNotOptimizeForBrowser/>
            </w:WordDocument>
        </xml>
        <![endif]-->
        <style>
            <!-- 
            /* Style Definitions */ 
            @page Section1 {{size:8.5in 11.0in; margin:1.0in 1.25in 1.0in 1.25in; mso-header-margin:.5in; mso-footer-margin:.5in; mso-paper-source:0;}} 
            div.Section1 {{page:Section1;}} 
            body {{ font-family: "Calibri", "Arial", sans-serif; font-size: 11pt; }}
            h1, h2, h3 {{ color: #2E74B5; }}
            code {{ font-family: "Consolas", monospace; background-color: #f0f0f0; padding: 2px 4px; }}
            pre {{ background-color: #f0f0f0; padding: 10px; border-radius: 4px; }}
            -->
        </style>
    </head>
    <body dir="{body_dir}">
        <div class="Section1" style="text-align: {text_align};">
            {html_body}
        </div>
    </body>
    </html>
    """
    return full_html

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    text = request.form.get('content', '')
    is_rtl = request.form.get('is_rtl') == 'on'
    html_content = process_text_to_html(text, is_rtl=is_rtl)
    
    file_stream = io.BytesIO()
    file_stream.write(html_content.encode('utf-8'))
    file_stream.seek(0)
    
    return send_file(
        file_stream,
        as_attachment=True,
        download_name="converted.doc",
        mimetype="application/msword"
    )

if __name__ == '__main__':
    app.run(debug=True)
