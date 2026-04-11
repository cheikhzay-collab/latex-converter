import re
from app import preprocess_copied_math

val = r"""3. Montrer que pour tout $x \in [1, +\infty[$ :
$$0 < g(x) \le \frac{3}{2x}$$"""

print("--- INPUT ---")
print(val)

processedVal = preprocess_copied_math(val)

print("\n--- AFTER PREPROCESSING ---")
print(processedVal)

if "[[1, +\\infty[" in processedVal:
    print("\n❌ BUG PERSISTS: Interval was incorrectly converted.")
elif "[1, +\\infty[" in processedVal:
    print("\n✅ SUCCESS: Interval preserved correctly.")
else:
    print("\n❓ UNKNOWN STATE: Could not find interval in output.")
