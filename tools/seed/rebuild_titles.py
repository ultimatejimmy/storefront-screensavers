import json
import os
from collections import defaultdict

c_file = 'tools/seed/candidates_reddit.json'
with open(c_file, 'r', encoding='utf-8') as f:
    cands = json.load(f)

# Group by base title
groups = defaultdict(list)
for c in cands:
    base = c['title'].replace(' (Gallery)', '')
    groups[base].append(c)

for base, items in groups.items():
    if len(items) > 1:
        for idx, item in enumerate(items, 1):
            item['title'] = f'{base} (Image {idx})'
    elif len(items) == 1:
        items[0]['title'] = base

with open(c_file, 'w', encoding='utf-8') as f:
    json.dump(cands, f, indent=2, ensure_ascii=False)

# Rebuild HTML
items_js = json.dumps(cands, indent=2, ensure_ascii=False)

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Storefront Screensavers - Reddit Review</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ background: #0f172a; color: #f8fafc; font-family: system-ui, sans-serif; margin: 0; padding: 20px; }}
    header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }}
    h1 {{ margin: 0; font-size: 1.4rem; }}
    .stats {{ color: #94a3b8; font-size: 0.9rem; margin-top: 4px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px; }}
    .card {{ background: #1e293b; border: 2px solid #334155; border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; transition: border-color 0.2s; }}
    .card.approved {{ border-color: #22c55e; }}
    .card.rejected {{ border-color: #ef4444; opacity: 0.4; filter: grayscale(80%); }}
    .card img {{ width: 100%; aspect-ratio: 3/4; object-fit: cover; display: block; background: #1e293b; }}
    .card-body {{ padding: 12px; flex: 1; display: flex; flex-direction: column; gap: 6px; }}
    .card-title {{ font-size: 0.95rem; font-weight: 600; color: #f1f5f9; margin: 0; }}
    .card-author {{ font-size: 0.8rem; color: #94a3b8; margin: 0; }}
    .badges {{ display: flex; gap: 6px; flex-wrap: wrap; }}
    .badge {{ padding: 2px 8px; font-size: 0.7rem; border-radius: 4px; background: #334155; color: #cbd5e1; }}
    .badge-lic {{ background: #0369a1; color: #bae6fd; }}
    .actions {{ display: flex; gap: 8px; margin-top: auto; padding-top: 8px; }}
    .actions button {{ flex: 1; padding: 8px; font-weight: 600; border-radius: 6px; border: none; cursor: pointer; font-size: 0.85rem; }}
    .btn-approve {{ background: #22c55e; color: #052e16; }}
    .btn-reject  {{ background: #ef4444; color: #450a0a; }}
    .btn-export  {{ background: #8b5cf6; color: #fff; padding: 10px 20px; border-radius: 8px; font-size: 0.9rem; border: none; cursor: pointer; font-weight: bold; white-space: nowrap; }}
  </style>
</head>
<body>
<header>
  <div>
    <h1>🖼 Reddit Screensaver Review</h1>
    <div class="stats" id="stats">Loading…</div>
  </div>
  <button class="btn-export" onclick="exportApproved()">💾 Export approved_reddit.json</button>
</header>
<div class="grid" id="grid"></div>
<script>
const candidates = {items_js};
const state = {{}};
candidates.forEach(c => state[c.id] = true);

function render() {{
  const grid = document.getElementById('grid');
  grid.innerHTML = '';
  let nApp = 0, nRej = 0;
  candidates.forEach(c => {{
    const app = state[c.id];
    app ? nApp++ : nRej++;
    const card = document.createElement('div');
    card.className = 'card ' + (app ? 'approved' : 'rejected');
    const safeTitle = c.title.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    const safeAuthor = c.author.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    card.innerHTML = `
      <img src="${{c.previewPath}}" alt="${{safeTitle}}" loading="lazy">
      <div class="card-body">
        <p class="card-title">${{safeTitle}}</p>
        <p class="card-author">${{safeAuthor}}</p>
        <div class="badges">
          <span class="badge">${{c.category}}</span>
          <span class="badge badge-lic"><a href="${{c.sourceUrl}}" target="_blank" style="color:inherit; text-decoration:none;">🔗 Original Post</a></span>
        </div>
        <div class="actions">
          <button class="btn-approve" onclick="set('${{c.id}}',true)">✅ Approve</button>
          <button class="btn-reject"  onclick="set('${{c.id}}',false)">❌ Reject</button>
        </div>
      </div>`;
    grid.appendChild(card);
  }});
  document.getElementById('stats').innerText =
    `${{candidates.length}} total  ·  ${{nApp}} approved  ·  ${{nRej}} rejected`;
}}

function set(id, v) {{ state[id] = v; render(); }}

function exportApproved() {{
  const list = candidates.filter(c => state[c.id]);
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify(list,null,2)], {{type:'application/json'}}));
  a.download = 'approved_reddit.json';
  a.click();
}}

render();
</script>
</body>
</html>
"""

with open('tools/seed/review_reddit.html', 'w', encoding='utf-8') as f:
    f.write(HTML)

print('Updated titles and rebuilt review_reddit.html without re-downloading!')
