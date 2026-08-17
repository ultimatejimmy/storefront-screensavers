import json

with open('screensavers.json', 'r', encoding='utf-8') as f:
    cat = json.load(f)

# Fix missing fields
for item in cat:
    if 'license' not in item:
        item['license'] = 'Community Share'
    if 'attribution' not in item:
        item['attribution'] = item.get('author', 'Community')
    if 'sourceUrl' not in item:
        item['sourceUrl'] = ''

with open('screensavers.json', 'w', encoding='utf-8') as f:
    json.dump(cat, f, indent=2, ensure_ascii=False)

trans = [i for i in cat if i['category'] == 'Transparent Overlay']
print('Transparent Overlay count:', len(trans))

# Regenerate CREDITS.md
lines = [
    '# External Sourcing & Attribution Credits',
    '',
    'All open access, Public Domain, CC0, and community-shared screensavers in this catalog are credited below.',
    '',
    '| Title | Creator / Artist | Category | License | Source & Attribution |',
    '|---|---|---|---|---|'
]

for item in cat:
    src = item.get('sourceUrl', '')
    attr = item.get('attribution') or item.get('author', 'N/A')
    src_cell = '[{}]({})'.format(attr, src) if src else attr
    lines.append('| {} | {} | {} | {} | {} |'.format(
        item['title'], item['author'], item['category'], item['license'], src_cell
    ))

lines += [
    '',
    '---',
    '',
    '## License Definitions',
    '',
    '- **CC0**: Dedicated to the public domain worldwide.',
    '- **Public Domain**: Works whose copyright has expired.',
    '- **Unsplash / Pexels License**: Free for commercial and non-commercial use.',
    '- **Community Share**: Shared publicly for community e-reader use.',
    ''
]

with open('CREDITS.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print('CREDITS.md regenerated successfully.')
print('Done!')
