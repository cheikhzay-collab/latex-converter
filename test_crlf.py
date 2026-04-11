"""Test: Does Windows CRLF (\r\n) break the multi-line bracket regex?"""
import re
from app import preprocess_copied_math

# Simulate exact Windows form textarea content with \r\n line endings
crlf_text = "Here is an example equation:\r\n\r\n[\r\n\\int_a^b x^2 \\, dx = \\frac{b^3 - a^3}{3}\r\n]\r\n\r\nAnd an inline one: (E = mc^2)."

# Compare with Unix \n
lf_text = crlf_text.replace('\r\n', '\n')

print("=== CRLF (Windows) via preprocess_copied_math ===")
result_crlf = preprocess_copied_math(crlf_text)
if '$$' in result_crlf:
    print("PASS: Display math converted")
else:
    print("FAIL: Display math NOT converted!")

if '$E = mc^2$' in result_crlf:
    print("PASS: Inline math converted")
else:
    print("FAIL: Inline math NOT converted!")

print("\nResult:")
print(result_crlf)

print("\n=== LF (Unix) via preprocess_copied_math ===")
result_lf = preprocess_copied_math(lf_text)
if '$$' in result_lf:
    print("PASS: Display math converted")
else:
    print("FAIL: Display math NOT converted!")
