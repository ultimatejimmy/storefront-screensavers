import os, json, shutil
from PIL import Image

SEED_DIR = r'C:\Users\Jimmy\Documents\Storefront\storefront-screensavers\tools\seed'
SRC_DIR = r'C:\Users\Jimmy\Downloads\Koreader screensavers'

REVIEW_THUMBS_DIR = os.path.join(SEED_DIR, 'review_thumbs_whisperingsea4')
CANDIDATES_FILE = os.path.join(SEED_DIR, 'candidates_whisperingsea4.json')
REVIEW_HTML = os.path.join(SEED_DIR, 'review_whisperingsea4.html')

if os.path.exists(REVIEW_THUMBS_DIR):
    shutil.rmtree(REVIEW_THUMBS_DIR, ignore_errors=True)
os.makedirs(REVIEW_THUMBS_DIR, exist_ok=True)

# List of all files
files = sorted(os.listdir(SRC_DIR))
print(f'Processing {len(files)} files for interactive review HTML...')

candidates = []
for idx, filename in enumerate(files, start=1):
    src_path = os.path.join(SRC_DIR, filename)
    cid = f'wss4-{idx:02d}'
    
    thumb_name = f'{cid}.jpg'
    thumb_path = os.path.join(REVIEW_THUMBS_DIR, thumb_name)
    rel_thumb_path = f'review_thumbs_whisperingsea4/{thumb_name}'
    
    try:
        with Image.open(src_path) as img:
            img = img.convert('RGB')
            img.thumbnail((400, 600), Image.Resampling.LANCZOS)
            img.save(thumb_path, 'JPEG', quality=85)
    except Exception as e:
        print(f'Error processing thumbnail for {filename}: {e}')
        continue
        
    candidates.append({
        'id': cid,
        'filename': filename,
        'title': f'WhisperingSea4 Screensaver {idx:02d} ({filename})',
        'author': 'u/WhisperingSea4',
        'authorUrl': 'https://reddit.com/r/koreader/comments/1kcsl0n/i_really_appreciate_the_screensavers_that/',
        'category': 'r/koreader',
        'sourceUrl': 'https://reddit.com/r/koreader/comments/1kcsl0n/i_really_appreciate_the_screensavers_that/',
        'license': 'Community Share',
        'licenseUrl': 'https://reddit.com/r/koreader/comments/1kcsl0n/i_really_appreciate_the_screensavers_that/',
        'attribution': 'r/koreader Community',
        'imageUrl': src_path,
        'previewPath': rel_thumb_path
    })

with open(CANDIDATES_FILE, 'w', encoding='utf-8') as f:
    json.dump(candidates, f, indent=2, ensure_ascii=False)

items_js = json.dumps(candidates, indent=2, ensure_ascii=False)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Storefront Screensavers - WhisperingSea4 Review</title>
  <style>
    * { box-sizing: border-box; }
    body { background: #0f172a; color: #f8fafc; font-family: system-ui, sans-serif; margin: 0; padding: 20px; }
    header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }
    h1 { margin: 0; font-size: 1.4rem; }
    .stats { color: #94a3b8; font-size: 0.9rem; margin-top: 4px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px; }
    .card { background: #1e293b; border: 2px solid #334155; border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; transition: border-color 0.2s; }
    .card.approved { border-color: #22c55e; }
    .card.rejected { border-color: #ef4444; opacity: 0.4; filter: grayscale(80%); }
    .card img { width: 100%; aspect-ratio: 3/4; object-fit: cover; display: block; background: #1e293b; }
    .card-body { padding: 12px; flex: 1; display: flex; flex-direction: column; gap: 6px; }
    .card-title { font-size: 0.95rem; font-weight: 600; color: #f1f5f9; margin: 0; word-break: break-all; }
    .card-author { font-size: 0.8rem; color: #94a3b8; margin: 0; }
    .badges { display: flex; gap: 6px; flex-wrap: wrap; }
    .badge { padding: 2px 8px; font-size: 0.7rem; border-radius: 4px; background: #334155; color: #cbd5e1; }
    .badge-lic { background: #0369a1; color: #bae6fd; }
    .actions { display: flex; gap: 8px; margin-top: auto; padding-top: 8px; }
    .actions button { flex: 1; padding: 8px; font-weight: 600; border-radius: 6px; border: none; cursor: pointer; font-size: 0.85rem; }
    .btn-approve { background: #22c55e; color: #052e16; }
    .btn-reject  { background: #ef4444; color: #450a0a; }
    .btn-export  { background: #8b5cf6; color: #fff; padding: 10px 20px; border-radius: 8px; font-size: 0.9rem; border: none; cursor: pointer; font-weight: bold; white-space: nowrap; }
  </style>
</head>
<body>
<header>
  <div>
    <h1>🖼 u/WhisperingSea4 Screensaver Review</h1>
    <div class="stats" id="stats">Loading…</div>
  </div>
  <button class="btn-export" onclick="exportApproved()">💾 Export approved_whisperingsea4.json</button>
</header>
<div class="grid" id="grid"></div>
<script>
const candidates = ITEMS_PLACEHOLDER;
const state = {};
candidates.forEach(c => state[c.id] = true);

function render() {
  const grid = document.getElementById('grid');
  grid.innerHTML = '';
  let nApp = 0, nRej = 0;
  candidates.forEach(c => {
    const app = state[c.id];
    app ? nApp++ : nRej++;
    const card = document.createElement('div');
    card.className = 'card ' + (app ? 'approved' : 'rejected');
    const safeTitle = c.title.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    const safeAuthor = c.author.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    card.innerHTML = `
      <img src="${c.previewPath}" alt="${safeTitle}" loading="lazy">
      <div class="card-body">
        <p class="card-title">${safeTitle}</p>
        <p class="card-author">${safeAuthor}</p>
        <div class="badges">
          <span class="badge">${c.category}</span>
          <span class="badge badge-lic"><a href="${c.sourceUrl}" target="_blank" style="color:inherit; text-decoration:none;">🔗 Reddit Post</a></span>
        </div>
        <div class="actions">
          <button class="btn-approve" onclick="set('${c.id}',true)">✅ Approve</button>
          <button class="btn-reject"  onclick="set('${c.id}',false)">❌ Reject</button>
        </div>
      </div>`;
    grid.appendChild(card);
  });
  document.getElementById('stats').innerText =
    `${candidates.length} total  ·  ${nApp} approved  ·  ${nRej} rejected`;
}

function set(id, v) { state[id] = v; render(); }

function exportApproved() {
  const list = candidates.filter(c => state[c.id]);
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify(list,null,2)], {type:'application/json'}));
  a.download = 'approved_whisperingsea4.json';
  a.click();
}

render();
</script>
</body>
</html>
"""

html_content = HTML_TEMPLATE.replace('ITEMS_PLACEHOLDER', items_js)

with open(REVIEW_HTML, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f'Successfully built review_whisperingsea4.html and generated {len(candidates)} review thumbnails!')
