import lxml.html

def test_multi(html):
    soup = lxml.html.fromstring(html)
    print(f"HTML: {html}")
    print(f"Root tag: {soup.tag}")
    elements = soup.xpath('//body/*') or soup.xpath('/*')
    print(f"Elements: {[e.tag for e in elements]}")

test_multi("<body><p>P1</p><p>P2</p></body>")
test_multi("<div><p>P1</p><p>P2</p></div>")
