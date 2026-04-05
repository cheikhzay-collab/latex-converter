import html
import io
import re
import markdown
import latex2mathml.converter
from flask import Flask, render_template, request, send_file, make_response, Response
from functools import wraps
import sqlite3
import uuid
import os
import datetime
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from lxml import etree
import lxml.html

app = Flask(__name__)

DB_PATH = 'stats.db'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS stats (id INTEGER PRIMARY KEY, downloads INTEGER, chars INTEGER, unique_users INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS daily_stats (date TEXT PRIMARY KEY, downloads INTEGER DEFAULT 0, chars INTEGER DEFAULT 0, unique_users INTEGER DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS users (visitor_id TEXT PRIMARY KEY, first_visit_date TEXT)''')
        conn.commit()

init_db()

# Path to MML2OMML.XSL found on user's system
XSLT_PATH = r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"

def preprocess_copied_math(text):
    """
    Cleans up common LLM math notation and fixes the 'Interval Bug'.
    """
    # 1. Standard LaTeX display: \[ ... \] -> $$ ... $$
    text = re.sub(r'\\\[([\s\S]*?)\\\]', r'$$\1$$', text)
    
    # 2. Heuristic for raw brackets [ ... ] on own line
    # We must AVOID matching intervals like [1, +\infty[
    def bracket_math_cleaner(match):
        content = match.group(1).strip()
        # French interval check: [digit, digit[ or [digit; digit]
        if re.search(r'^[\d., \-+]+[ \t]*[,;][ \t]*[\d., \-+\\infty]+[\[\]]?$', content):
            return match.group(0) # Keep as is
        # Strong math indicator: contains \, ^, _, =, or is long
        if re.search(r'[\^\\=_]|\d+[a-z]|\\frac', content) or len(content) > 15:
            return f"$${content}$$"
        return match.group(0)

    text = re.sub(r'(?m)^[ \t]*\[([^\[\]\n]+)\][ \t]*$', bracket_math_cleaner, text)
    
    # 3. Double parentheses ((C_f)) -> \(C_f\)
    text = re.sub(r'\(\((.*?)\)\)', r'\(\1\)', text)
    
    # 4. Remove AI citation markers
    text = re.sub(r'\[cite[_:][^\]]*\]', '', text)
    return text

def get_omml(latex):
    """Converts LaTeX to OMML XML element using MML2OMML.XSL."""
    try:
        mathml = latex2mathml.converter.convert(latex)
        # Parse MathML
        mml_root = etree.fromstring(mathml.encode('utf-8'))
        
        # Load XSLT
        xslt_tree = etree.parse(XSLT_PATH)
        transform = etree.XSLT(xslt_tree)
        
        # Transform to OMML
        omml_tree = transform(mml_root)
        # Convert to string for python-docx to parse
        omml_str = etree.tostring(omml_tree)
        return parse_xml(omml_str)
    except Exception as e:
        print(f"OMML Conversion Error: {e}")
        return None

def add_math_to_run(paragraph, latex, is_display=False):
    """Inserts a native Math object into a paragraph."""
    if is_display:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
    omml_node = get_omml(latex)
    if omml_node is not None:
        paragraph._element.append(omml_node)
    else:
        # Fallback to red text if conversion fails
        run = paragraph.add_run(f"[Math Error: {latex}]")
        run.font.color.rgb = RGBColor(255, 0, 0)

def html_to_docx(html_content, document, is_rtl=False):
    """
    Maps HTML elements (from markdown) to python-docx elements.
    Handles math placeholders ($$ and $).
    """
    if not html_content.strip():
        return
        
    try:
        # We wrap in a div and use fromstring to ensure all fragments are captured
        fragment = lxml.html.fromstring(f"<div>{html_content}</div>")
        elements = fragment.xpath('./*') # Get direct children (p, h1, ul, etc.)
    except Exception as e:
        print(f"HTML Parse Error: {e}")
        return

    if not elements:
        print("No elements found in HTML content")
        return
    
    for element in elements:
        tag = element.tag
        
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag[1])
            p = document.add_heading('', level=level)
            if is_rtl: p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            process_inline(element, p)
            
        elif tag == 'p':
            p = document.add_paragraph()
            if is_rtl: p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            process_inline(element, p)
            
        elif tag in ['ul', 'ol']:
            for li in element.xpath('.//li'):
                p = document.add_paragraph(style='List Bullet' if tag == 'ul' else 'List Number')
                if is_rtl: p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                process_inline(li, p)
        
        elif tag == 'table':
            rows = element.xpath('.//tr')
            if not rows: continue
            cells_in_first_row = rows[0].xpath('./td|./th')
            cols_count = len(cells_in_first_row)
            if cols_count == 0: continue
            
            table = document.add_table(rows=0, cols=cols_count)
            table.style = 'Table Grid'
            for row_el in rows:
                cells = row_el.xpath('./td|./th')
                row = table.add_row()
                for i, cell_el in enumerate(cells):
                    if i < len(row.cells):
                        p = row.cells[i].paragraphs[0]
                        if is_rtl: p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                        process_inline(cell_el, p)

def process_inline(element, paragraph):
    """Processes text nodes and inline math within an element."""
    inner_html = lxml.html.tostring(element, encoding='unicode', method='html')
    start = inner_html.find('>') + 1
    end = inner_html.rfind('<')
    inner_content = inner_html[start:end] if start < end else element.text_content()

    # Remove <br> tags inside math delimiters so they don't break math parsing
    # Handle display math $$...$$ first, then inline math $...$
    def strip_br_in_math(m):
        return re.sub(r'<br\s*/?>', ' ', m.group(0))
    inner_content = re.sub(r'\$\$[\s\S]*?\$\$', strip_br_in_math, inner_content)
    inner_content = re.sub(r'\$[^\$\n]+?\$', strip_br_in_math, inner_content)

    # Split into sections of text, display math ($$), and inline math ($)
    parts = re.split(r'(\$\$[\s\S]*?\$\$|\$[^\$\n]+?\$)', inner_content)
    
    for part in parts:
        if not part: continue
        if part.startswith('$$') and part.endswith('$$'):
            # Unescape LaTeX display math
            latex = html.unescape(part[2:-2])
            add_math_to_run(paragraph, latex, is_display=False)
        elif part.startswith('$') and part.endswith('$'):
            # Unescape LaTeX inline math
            latex = html.unescape(part[1:-1])
            add_math_to_run(paragraph, latex, is_display=False)
        else:
            # Clean text and add to run
            clean_text = re.sub(r'<br\s*/?>', '\n', part)
            clean_text = re.sub(r'<[^>]+>', '', clean_text)
            clean_text = html.unescape(clean_text)
            paragraph.add_run(clean_text)

@app.route('/')
def index():
    visitor_id = request.cookies.get('visitor_id')
    response = make_response(render_template('index.html'))
    
    if not visitor_id:
        visitor_id = str(uuid.uuid4())
        response.set_cookie('visitor_id', visitor_id, max_age=60*60*24*365) # 1 year
        today = datetime.date.today().isoformat()
        try:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute('INSERT OR IGNORE INTO users (visitor_id, first_visit_date) VALUES (?, ?)', (visitor_id, today))
                if c.rowcount > 0:
                    c.execute('INSERT OR IGNORE INTO daily_stats (date, downloads, chars, unique_users) VALUES (?, 0, 0, 0)', (today,))
                    c.execute('UPDATE daily_stats SET unique_users = unique_users + 1 WHERE date = ?', (today,))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database error tracking user: {e}")

    return response

@app.route('/convert', methods=['POST'])
def convert():
    content = request.form.get('content', '')
    is_rtl = request.form.get('is_rtl') == 'on'
    
    # 1. Preprocess
    clean_text = preprocess_copied_math(content)
    
    # 2. Convert to HTML via Markdown
    html_body = markdown.markdown(clean_text, extensions=['extra', 'nl2br'])
    
    # 3. Create Document
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    # 4. Map HTML to Docx
    html_to_docx(f"<body>{html_body}</body>", doc, is_rtl=is_rtl)
    
    # 5. Save and Return
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    
    # 6. Update Stats
    try:
        chars_count = len(content)
        today = datetime.date.today().isoformat()
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('INSERT OR IGNORE INTO daily_stats (date, downloads, chars, unique_users) VALUES (?, 0, 0, 0)', (today,))
            c.execute('UPDATE daily_stats SET downloads = downloads + 1, chars = chars + ? WHERE date = ?', (chars_count, today))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error updating stats: {e}")
    
    return send_file(
        file_stream,
        as_attachment=True,
        download_name="converted.docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

def check_auth(username, password):
    return username == 'admin' and password == '123456'

def authenticate():
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Admin Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/admin')
@requires_auth
def admin():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            # Global totals
            c.execute('SELECT SUM(unique_users), SUM(downloads), SUM(chars) FROM daily_stats')
            totals = c.fetchone()
            if not totals or totals[0] is None:
                totals = (0, 0, 0)
                
            # History
            c.execute('SELECT date, unique_users, downloads FROM daily_stats ORDER BY date DESC LIMIT 14')
            history = [{'date': row[0], 'users': row[1], 'downloads': row[2]} for row in c.fetchall()]
            history.reverse()
    except sqlite3.Error:
        totals = (0, 0, 0)
        history = []
        
    return render_template('admin.html', stats={
        'users': totals[0],
        'downloads': totals[1],
        'chars': totals[2],
        'history': history,
        'today': datetime.date.today().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True)
