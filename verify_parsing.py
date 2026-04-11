import re

def test_parsing():
    text = """Here is a formula:
$$ x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} $$
And inline: $E=mc^2$
And another block:
\\[ a^2 + b^2 = c^2 \\]
End of text."""

    print("--- Original Text ---")
    print(text)
    print("---------------------")

    # The regex from app.py
    pattern = re.compile(r'(\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\$[^\$\n]+\$|\\\(.*?\\\))')
    
    parts = pattern.split(text)
    
    print(f"Found {len(parts)} parts.")
    for i, part in enumerate(parts):
        print(f"Part {i}: '{part}'")

if __name__ == "__main__":
    test_parsing()
