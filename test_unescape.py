import html
import re

def test_unescape():
    # Test cases showing common LaTeX inside HTML-escaped fragments
    test_cases = [
        ("$x < y$", "x < y"),
        ("$x > 0$", "x > 0"),
        ("$\\forall x \\ge 1, \\quad 0 < f(x) \\le \\frac{3}{2x^3}$", "\\forall x \\ge 1, \\quad 0 < f(x) \\le \\frac{3}{2x^3}")
    ]
    
    for case, expected in test_cases:
        # Simulate what markdown might do (escaping < and >)
        escaped = case.replace("<", "&lt;").replace(">", "&gt;")
        print(f"Escaped: {escaped}")
        
        # Simulate our fix
        if escaped.startswith('$$') and escaped.endswith('$$'):
            latex = html.unescape(escaped[2:-2])
        elif escaped.startswith('$') and escaped.endswith('$'):
            latex = html.unescape(escaped[1:-1])
        else:
            latex = html.unescape(escaped)
            
        print(f"Unescaped: {latex}")
        assert latex == expected
        print("PASS")

if __name__ == "__main__":
    test_unescape()
