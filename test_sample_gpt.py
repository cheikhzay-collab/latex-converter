"""Test script to verify how the converter handles raw ChatGPT-copied content 
with bare bracket/parenthesis math delimiters."""

import sys
sys.path.insert(0, '.')
from app import preprocess_copied_math, clean_raw_brackets

sample = r"""# **Integration Formula**

Here is an example equation:

[
\int_a^b x^2 \, dx = \frac{b^3 - a^3}{3}
]

And an inline one: (E = mc^2).

## **Properties**

* The function is **continuous** on ([a, b])
* The derivative: (f'(x) = 2x)
* A table:

**Variable** | **Value**
a | 0
b | 1
"""

print("=" * 60)
print("INPUT:")
print(sample)
print("=" * 60)

# Step 1: Test bracket cleaning alone
step1 = clean_raw_brackets(sample)
print("\nSTEP 1 - clean_raw_brackets:")
for line in step1.splitlines():
    if '$' in line or '\\' in line:
        print(f"  >> {line}")

# Step 2: Full preprocessing  
result = preprocess_copied_math(sample)
print("\n" + "=" * 60)
print("FINAL OUTPUT:")
print(result)
print("=" * 60)

# Verify key conversions
checks = [
    ("Display math converted", "$$" in result and "\\int" in result),
    ("Inline E=mc^2 converted", "$E = mc^2$" in result),
    ("Inline derivative converted", "$f'(x) = 2x$" in result),
    ("Interval [a, b] preserved", "[a, b]" in result or "$a, b$" not in result),
]

print("\nVERIFICATION:")
for name, passed in checks:
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"  {status}: {name}")
