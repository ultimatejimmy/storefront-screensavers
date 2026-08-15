import json
import urllib.request
import time
import os

print("[+] Fixing Transparent titles...")
c_file_trans = 'tools/seed/candidates_transparent.json'
with open(c_file_trans, 'r', encoding='utf-8') as f:
    cands_trans = json.load(f)

trans_mapping = {
    'Transparent KOReader Overlay 3': 'Cat Looking Out Window',
    'Transparent KOReader Overlay 4': 'Spirited Away Dragon Haku',
    'Transparent KOReader Overlay 5': 'Frieren and Fern',
    'Transparent KOReader Overlay 11': 'Garfield Reading Book',
    'Transparent KOReader Overlay 18': 'Reading a Newspaper Engraving',
    'Transparent KOReader Overlay 19': 'Baymax Waving',
    'Transparent KOReader Overlay 20': 'Marvel Superheroes Cover'
}

for c in cands_trans:
    if c['title'] in trans_mapping:
        c['title'] = trans_mapping[c['title']]

with open(c_file_trans, 'w', encoding='utf-8') as f:
    json.dump(cands_trans, f, indent=2, ensure_ascii=False)

items_trans_js = json.dumps(cands_trans, indent=2, ensure_ascii=False)
with open('tools/seed/build_readerbackdrop_seed_batch.py', 'r', encoding='utf-8') as f:
    content = f.read()

html_start = content.find('HTML = f"""') + 11
html_end = content.find('"""', html_start)
html_template = content[html_start:html_end]
html_out = html_template.replace('{items_js}', items_trans_js).replace('{{', '{').replace('}}', '}')

with open('tools/seed/review_transparent.html', 'w', encoding='utf-8') as f:
    f.write(html_out)


print("\n[+] Fixing Wallhaven titles by fetching tags...")
c_file = 'tools/seed/candidates_wallhaven.json'
with open(c_file, 'r', encoding='utf-8') as f:
    cands = json.load(f)

for idx, c in enumerate(cands, 1):
    if "Wallpaper" not in c['title']:
        continue
    wh_id = c['id'].replace('wh-', '')
    url = f'https://wallhaven.cc/api/v1/w/{wh_id}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())['data']
            tags = [t['name'].title() for t in data.get('tags', [])][:3]
            if tags:
                c['title'] = ' '.join(tags)
                print(f"[{idx}/{len(cands)}] Renamed to: {c['title']}")
    except Exception as e:
        print(f"Error on {wh_id}: {e}")
    time.sleep(1.5)

with open(c_file, 'w', encoding='utf-8') as f:
    json.dump(cands, f, indent=2, ensure_ascii=False)

items_js = json.dumps(cands, indent=2, ensure_ascii=False)
with open('tools/seed/build_wallhaven_seed_batch.py', 'r', encoding='utf-8') as f:
    content = f.read()

html_start = content.find('HTML = f"""') + 11
html_end = content.find('"""', html_start)
html_template = content[html_start:html_end]
html_out = html_template.replace('{items_js}', items_js).replace('{{', '{').replace('}}', '}')

with open('tools/seed/review_wallhaven.html', 'w', encoding='utf-8') as f:
    f.write(html_out)
    
print("Done fixing all titles!")
