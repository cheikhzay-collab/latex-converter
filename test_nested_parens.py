import re

def safe_paren_math_cleaner(text):
    # Temporarily hide $...$, $$...$$, \[...\], \(...\)
    hidden = {}
    counter = 0

    def hide(match):
        nonlocal counter
        key = f"__MATH_{counter}__"
        hidden[key] = match.group(0)
        counter += 1
        return key

    # Hide $$...$$
    text = re.sub(r'\$\$[\s\S]*?\$\$', hide, text)
    # Hide \[...\]
    text = re.sub(r'\\\[[\s\S]*?\\\]', hide, text)
    # Hide \(...\)
    text = re.sub(r'\\\([\s\S]*?\\\)', hide, text)
    # Hide $...$
    text = re.sub(r'\$[\s\S]*?\$', hide, text)
    
    # Now run paren_math_cleaner on the rest
    def paren_math_cleaner(match):
        content = match.group(1).strip()
        if re.search(r'[\^\\=_]', content) and len(content) > 3:
            return f"${content}$"
        return match.group(0)

    text = re.sub(r'(?<!\\)\(((?:[^()]|\([^()]*\))*)\)', paren_math_cleaner, text)
    
    # Restore hidden math
    for key, val in hidden.items():
        text = text.replace(key, val)
        
    return text

text = r"""
1. Définition et Dérivabilité en un Point

*   **Définition Globale :** Une fonction $f$ est dite dérivable en $x_0$ si la limite $\lim_{x \to x_0} \frac{f(x) - f(x_{0})}{x - x_0}$ existe et est finie.
*   **Nombre Dérivé :** Cette limite est notée $f'(x_{0})$.
*   **Équation de la Tangente :** Au point d'abscisse $x_0$, elle est donnée par $y = f'(x_{0})(x - x_{0}) + f(x_{0})$.

Here is a raw one: (E = mc^2)
"""

print(safe_paren_math_cleaner(text))
