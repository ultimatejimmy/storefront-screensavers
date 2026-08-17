import os
import json
import requests
from PIL import Image, ImageOps
from io import BytesIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CANDIDATES_FILE = os.path.join(BASE_DIR, 'candidates.json')
REVIEW_DIR = os.path.join(BASE_DIR, 'review_thumbs')
REVIEW_HTML = os.path.join(BASE_DIR, 'review.html')

os.makedirs(REVIEW_DIR, exist_ok=True)

with open(CANDIDATES_FILE, 'r', encoding='utf-8') as f:
    candidates = json.load(f)

print(f"Loaded {len(candidates)} candidates from candidates.json")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

downloaded_candidates = []

for idx, item in enumerate(candidates):
    thumb_filename = f"{item['id']}.jpg"
    thumb_path = os.path.join(REVIEW_DIR, thumb_filename)
    rel_thumb_path = f"review_thumbs/{thumb_filename}"
    
    print(f"[{idx+1}/{len(candidates)}] Processing '{item['title']}'...")
    
    if os.path.exists(thumb_path):
        print(f"  -> Thumbnail already cached.")
        item['localThumbUrl'] = rel_thumb_path
        downloaded_candidates.append(item)
        continue

    try:
        r = requests.get(item['imageUrl'], headers=headers, timeout=15)
        if r.status_code == 200:
            img = Image.open(BytesIO(r.content))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Crop 3:4 review thumbnail (450x600)
            thumb = ImageOps.fit(img, (450, 600), Image.Resampling.LANCZOS)
            thumb.save(thumb_path, 'JPEG', quality=85)
            
            item['localThumbUrl'] = rel_thumb_path
            downloaded_candidates.append(item)
            print(f"  -> Successfully downloaded & generated thumbnail.")
        else:
            print(f"  -> HTTP Error {r.status_code} loading image.")
    except Exception as e:
        print(f"  -> Exception loading image: {e}")

# Generate review.html
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Candidate Screensavers Review & Approval Tool</title>
  <style>
    body {{
      font-family: system-ui, -apple-system, sans-serif;
      background: #0f172a;
      color: #f8fafc;
      margin: 0;
      padding: 2rem;
    }}
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
      border-bottom: 1px solid #334155;
      padding-bottom: 1rem;
    }}
    h1 {{ margin: 0; font-size: 1.8rem; background: linear-gradient(135deg, #a855f7, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .stats {{ font-size: 1.1rem; color: #94a3b8; }}
    .btn-export {{
      background: #8b5cf6;
      color: white;
      border: none;
      padding: 0.75rem 1.5rem;
      border-radius: 8px;
      font-weight: 600;
      font-size: 1rem;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
      transition: all 0.2s;
    }}
    .btn-export:hover {{ background: #7c3aed; transform: translateY(-2px); }}
    
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 1.5rem;
    }}
    .card {{
      background: #1e293b;
      border: 2px solid #334155;
      border-radius: 12px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: all 0.2s;
    }}
    .card.approved {{ border-color: #22c55e; }}
    .card.rejected {{ border-color: #ef4444; opacity: 0.45; }}
    .img-wrap {{ aspect-ratio: 3/4; overflow: hidden; background: #000; position: relative; }}
    .img-wrap img {{ width: 100%; height: 100%; object-fit: cover; }}
    .body {{ padding: 1rem; flex: 1; display: flex; flex-direction: column; gap: 0.4rem; }}
    .title {{ font-size: 1rem; font-weight: 600; color: #f8fafc; margin: 0; }}
    .author {{ font-size: 0.85rem; color: #94a3b8; }}
    .meta {{ display: flex; justify-content: space-between; font-size: 0.8rem; color: #cbd5e1; margin-top: 0.3rem; }}
    .tag {{ background: rgba(6, 182, 212, 0.15); color: #22d3ee; padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 600; font-size: 0.75rem; text-decoration: none; display: inline-block; }}
    .actions {{ display: flex; gap: 0.5rem; margin-top: 0.75rem; }}
    .btn-action {{
      flex: 1;
      padding: 0.5rem;
      border: none;
      border-radius: 6px;
      font-weight: 600;
      font-size: 0.85rem;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .btn-approve {{ background: #15803d; color: white; }}
    .btn-approve.active {{ background: #22c55e; box-shadow: 0 0 10px rgba(34, 197, 94, 0.5); }}
    .btn-reject {{ background: #991b1b; color: white; }}
    .btn-reject.active {{ background: #ef4444; box-shadow: 0 0 10px rgba(239, 68, 68, 0.5); }}
  </style>
</head>
<body>

  <div class="header">
    <div>
      <h1>Candidate Screensavers Review & Approval Tool</h1>
      <div class="stats">Showing <span id="count-total">{len(downloaded_candidates)}</span> candidates (<span id="count-approved" style="color: #22c55e;">{len(downloaded_candidates)}</span> approved, <span id="count-rejected" style="color: #ef4444;">0</span> rejected)</div>
    </div>
    <button id="btn-export" class="btn-export">💾 Save approved.json & Commit →</button>
  </div>

  <div class="grid" id="grid"></div>

  <script>
    const items = {json.dumps(downloaded_candidates, indent=2)};
    const statusMap = {{}};

    // Default all items to approved
    items.forEach(item => {{
      statusMap[item.id] = 'approved';
    }});

    function updateCounts() {{
      const total = items.length;
      const approved = Object.values(statusMap).filter(s => s === 'approved').length;
      const rejected = Object.values(statusMap).filter(s => s === 'rejected').length;
      
      document.getElementById('count-total').textContent = total;
      document.getElementById('count-approved').textContent = approved;
      document.getElementById('count-rejected').textContent = rejected;
    }}

    function renderGrid() {{
      const grid = document.getElementById('grid');
      grid.innerHTML = '';

      items.forEach(item => {{
        const status = statusMap[item.id] || 'approved';
        const card = document.createElement('div');
        card.className = `card ${{status}}`;
        card.innerHTML = `
          <div class="img-wrap">
            <img src="${{item.localThumbUrl}}" alt="${{item.title}}">
          </div>
          <div class="body">
            <h4 class="title">${{item.title}}</h4>
            <div class="author">by ${{item.author}}</div>
            <div class="meta">
              <span>🏷️ ${{item.category}}</span>
              <a href="${{item.sourceUrl}}" target="_blank" class="tag">${{item.license}}</a>
            </div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.2rem;">${{item.attribution || ''}}</div>
            <div class="actions">
              <button class="btn-action btn-approve ${{status === 'approved' ? 'active' : ''}}" onclick="setStatus('${{item.id}}', 'approved')">✅ Approve</button>
              <button class="btn-action btn-reject ${{status === 'rejected' ? 'active' : ''}}" onclick="setStatus('${{item.id}}', 'rejected')">❌ Reject</button>
            </div>
          </div>
        `;
        grid.appendChild(card);
      }});

      updateCounts();
    }}

    window.setStatus = function(id, status) {{
      statusMap[id] = status;
      renderGrid();
    }};

    document.getElementById('btn-export').addEventListener('click', () => {{
      const approvedItems = items.filter(item => statusMap[item.id] === 'approved');
      const jsonStr = JSON.stringify(approvedItems, null, 2);
      
      const blob = new Blob([jsonStr], {{ type: 'application/json' }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'approved.json';
      a.click();

      alert(`Exported ${{approvedItems.length}} approved screensavers to approved.json!\n\nNext step: Place approved.json in tools/seed/ and run commit_approved.py.`);
    }});

    renderGrid();
  </script>
</body>
</html>
"""

with open(REVIEW_HTML, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n[+] Review tool generated successfully!")
print(f"[+] Open review tool in browser: file:///{REVIEW_HTML.replace('\\\\', '/')}")
