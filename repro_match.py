import re
text = "f(x) = 3x^2"
text = re.sub(r'\(([A-Za-z])\)', r'\(\1\)', text)
print("AFTER PREPROCESS:", repr(text))

pattern = re.compile(r'(\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\$[^\$\n]+\$|\\\([\s\S]*?\\\))')
matches = pattern.findall(text)
print("MATCHES:", matches)
