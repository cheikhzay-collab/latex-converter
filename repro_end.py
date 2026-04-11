import re

text = r"""Voici le texte extrait de l’image :

---

# **Integration Formula**

Here is an example equation:

[
\int_a^b x^2 , dx = \frac{b^3 - a^3}{3}
]

And an inline one: (E = mc^2).

## **Properties**

* The function is **continuous** on ([a, b])
* The derivative: (f'(x) = 2x)
* A table:

**Variable** | **Value**
a | 0
b | 1

---"""

def bracket_math_cleaner(match):
    content = match.group(1).strip()
    # French interval check: [digit, digit[ or [digit; digit]
    if re.search(r'^[\d., \-+]+[ \t]*[,;][ \t]*[\d., \-+\\infty]+[\[\]]?$', content):
        return match.group(0) # Keep as is
    # Strong math indicator
    if re.search(r'[\^\\=_]|\d+[a-z]|\\frac|\\int|\\sum|\\lim', content) or len(content) > 15:
        return f"$${content}$$"
    return match.group(0)

# single-line
text = re.sub(r'(?m)^[ \t]*\[([^\[\]\n]+)\][ \t]*$', bracket_math_cleaner, text)
# multi-line
text = re.sub(r'(?m)^[ \t]*\[\s*\n([\s\S]*?)\n[ \t]*\][ \t]*$', bracket_math_cleaner, text)

def paren_math_cleaner(match):
    content = match.group(1).strip()
    # Math indicator check
    if re.search(r'[\^\\=_]', content) and len(content) > 3:
        return f"${content}$"
    return match.group(0)

text = re.sub(r'\(([^\n()]+)\)', paren_math_cleaner, text)

print(text)
