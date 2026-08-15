"""patch2.py — fixes the Norwegian fjord and adds 3 more entries to reach 70+"""
import os

path = os.path.join(os.path.dirname(__file__), 'build_large_seed_batch.py')
with open(path, 'r', encoding='utf-8') as f:
    src = f.read()

# Find & replace whatever URL is currently in the nat-norway-fjord entry
import re
src = re.sub(
    r'("nat-norway-fjord".*?)"https://[^"]*?"',
    r'\1"https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=1200&q=80&fit=crop"',
    src, flags=re.DOTALL
)
print("Patched Norwegian fjord URL")

# Also add 3 more entries before the closing ] of RAW
EXTRA = """
    (
        "nat-rice-terraces",
        "Bali Rice Terraces",
        "Unsplash / Alfiano Sutianto",
        "Nature", "Unsplash License", "Unsplash",
        "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=1200&q=80&fit=crop",
    ),
    (
        "arch-colosseum",
        "Rome Colosseum at Dusk",
        "Unsplash / Henrique Ferreira",
        "Architecture", "Unsplash License", "Unsplash",
        "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=1200&q=80&fit=crop",
    ),
    (
        "min-black-sand-beach",
        "Black Sand Beach Iceland",
        "Unsplash / Jeremy Bishop",
        "Minimalist", "Unsplash License", "Unsplash",
        "https://images.unsplash.com/photo-1548438294-1ad5d5f4f063?w=1200&q=80&fit=crop",
    ),

"""

INSERT_BEFORE = "\n]\n\n# -----------"
if INSERT_BEFORE in src:
    src = src.replace(INSERT_BEFORE, EXTRA + INSERT_BEFORE, 1)
    print("Appended 3 more entries")

with open(path, 'w', encoding='utf-8') as f:
    f.write(src)
print("Done.")
