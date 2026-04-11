import lxml.html
from docx import Document

def test_xpath(html_content):
    soup = lxml.html.fromstring(html_content)
    elements = soup.xpath('//body/*') or soup.xpath('/*')
    print(f"Content: {html_content}")
    print(f"Soup tag: {soup.tag}")
    print(f"Elements found: {len(elements)}")
    for e in elements:
        print(f"  Tag: {e.tag}")

test_xpath("<body><p>Hello</p></body>")
test_xpath("<p>Hello</p>")
