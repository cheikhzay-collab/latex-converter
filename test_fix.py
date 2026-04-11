import lxml.html

def test_fix(html_body):
    html_content = f"<div>{html_body}</div>"
    soup = lxml.html.fromstring(html_content)
    print(f"Content: {html_content}")
    print(f"Soup tag: {soup.tag}")
    elements = soup.xpath('./*') # Get direct children of the div
    print(f"Children: {[e.tag for e in elements]}")

test_fix("<p>P1</p><p>P2</p>")
test_fix("<h1>H1</h1><p>P</p>")
