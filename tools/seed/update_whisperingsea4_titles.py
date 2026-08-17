import os, json
from PIL import Image

SEED_DIR = r'C:\Users\Jimmy\Documents\Storefront\storefront-screensavers\tools\seed'
SRC_DIR = r'C:\Users\Jimmy\Downloads\Koreader screensavers'
REVIEW_HTML = os.path.join(SEED_DIR, 'review_whisperingsea4.html')
CANDIDATES_FILE = os.path.join(SEED_DIR, 'candidates_whisperingsea4.json')
REVIEW_THUMBS_DIR = os.path.join(SEED_DIR, 'review_thumbs_whisperingsea4')

# Titles map matching the inventory we crafted
title_map = {
    'appa volando_0.png': ('Appa Soaring', 'whisperingsea4-appa-soaring', 'Pop Culture, Art'),
    'f-01.png': ('Solitary Mountain Peak', 'whisperingsea4-solitary-mountain-peak', 'Nature, Minimalist'),
    'f-02.png': ('Forest Canopy Starlight', 'whisperingsea4-forest-canopy-starlight', 'Nature, Fantasy'),
    'f-03.png': ('Misty Pine Ridge', 'whisperingsea4-misty-pine-ridge', 'Nature'),
    'f-04.png': ('Lunar Celestial Eclipse', 'whisperingsea4-lunar-celestial-eclipse', 'Abstract, Sci-Fi'),
    'f-05.png': ('Detailed Botanical Ferns', 'whisperingsea4-detailed-botanical-ferns', 'Nature, Minimalist'),
    'f-06.png': ('Floating Island Sanctuary', 'whisperingsea4-floating-island-sanctuary', 'Fantasy, Sci-Fi'),
    'f-07.png': ('Minimalist Dune Horizon', 'whisperingsea4-minimalist-dune-horizon', 'Minimalist, Nature'),
    'f-08.png': ('Minimalist Geometric Line Art Overlay', 'whisperingsea4-minimalist-geometric-line', 'Minimalist, Transparent'),
    'f-09.png': ('Ink-Wash Wave Crest', 'whisperingsea4-ink-wash-wave-crest', 'Art, Nature'),
    'f-10.png': ('Crescent Moon Reader', 'whisperingsea4-crescent-moon-reader', 'Minimalist, Art'),
    'f-11.png': ('Starry Sky Valley', 'whisperingsea4-starry-sky-valley', 'Nature, Fantasy'),
    'fondo-09.png': ('Serene Bamboo Grove', 'whisperingsea4-serene-bamboo-grove', 'Nature, Art'),
    'fondop_0000_bb37cb28197a0af997a573d947173819.png': ('Dark Celestial Constellations', 'whisperingsea4-dark-celestial-constellations', 'Sci-Fi, Abstract'),
    'fondop_0006.png': ('Mountain Sunset Silhouette', 'whisperingsea4-mountain-sunset-silhouette', 'Nature, Minimalist'),
    'fondop_0006_15.png': ('Cozy Coffee & Open Book', 'whisperingsea4-cozy-coffee-open-book', 'Minimalist, Cozy'),
    'fondop_0007.png': ('Starlight Forest Vista', 'whisperingsea4-starlight-forest-vista', 'Nature'),
    'fondop_0008_13.png': ('Midnight Sea Lighthouse', 'whisperingsea4-midnight-sea-lighthouse', 'Nature, Fantasy'),
    'fondop_0009_12.png': ('Deep Space Galaxy Swirl', 'whisperingsea4-deep-space-galaxy-swirl', 'Sci-Fi'),
    'fondop_0011_10.png': ('Geometric Topographic Lines', 'whisperingsea4-geometric-topographic-lines', 'Abstract, Minimalist'),
    'fondop_0012_9.png': ('Minimalist Wildflowers', 'whisperingsea4-minimalist-wildflowers', 'Nature, Minimalist'),
    'fondop_0013_8.png': ('Japanese Castle Under Moon', 'whisperingsea4-japanese-castle-under-moon', 'Architecture, Art'),
    'fondop_0016_5.png': ('Sunlit Pine Woods', 'whisperingsea4-sunlit-pine-woods', 'Nature'),
    'fondop_0018_3.png': ('Desert Night Dunes', 'whisperingsea4-desert-night-dunes', 'Nature, Minimalist'),
    'fondop_011.png': ('Forest River Reflections', 'whisperingsea4-forest-river-reflections', 'Nature'),
    'fondop_012.png': ('High Contrast Cloudscape', 'whisperingsea4-high-contrast-cloudscape', 'Nature, Minimalist'),
    'fondop_04.png': ('Atmospheric Mist Valley', 'whisperingsea4-atmospheric-mist-valley', 'Nature'),
    'fondos-04.png': ('Geometric Mandala Pattern', 'whisperingsea4-geometric-mandala-pattern', 'Abstract'),
    'Fondo2_1.png': ('Monochrome Ink Landscape I', 'whisperingsea4-monochrome-ink-landscape-1', 'Art, Nature'),
    'Fondo2_2.png': ('Monochrome Ink Landscape II', 'whisperingsea4-monochrome-ink-landscape-2', 'Art, Nature'),
    'Fondo2_3.png': ('Cosmic Portal Horizon', 'whisperingsea4-cosmic-portal-horizon', 'Sci-Fi, Abstract'),
    'Fondo2_4.png': ('Solitary Tree in Fog', 'whisperingsea4-solitary-tree-in-fog', 'Nature, Minimalist'),
    'Fondo2_5.png': ('Quiet Woodland Path', 'whisperingsea4-quiet-woodland-path', 'Nature'),
    'Fondo2_6.png': ('Crescent Moon & Waves', 'whisperingsea4-crescent-moon-waves', 'Minimalist, Nature'),
    'Fondo2_7.png': ('Minimalist Floral Stems', 'whisperingsea4-minimalist-floral-stems', 'Minimalist, Nature'),
    'Fondo2_9.png': ('Mountain Ridge Line Art', 'whisperingsea4-mountain-ridge-line-art', 'Nature, Minimalist'),
    'Fondo2_10.png': ('Starry Forest Night', 'whisperingsea4-starry-forest-night', 'Nature, Fantasy'),
    'Fondo2_11.png': ('Ocean Wave Stipple Art', 'whisperingsea4-ocean-wave-stipple-art', 'Art, Nature'),
    'Fondo2_12.png': ('Deep Forest Fog', 'whisperingsea4-deep-forest-fog', 'Nature'),
    'Fondo2_13.png': ('Geometric Lunar Cycles', 'whisperingsea4-geometric-lunar-cycles', 'Abstract, Minimalist'),
    'Fondo2_15.png': ('Mountain Lake Reflection', 'whisperingsea4-mountain-lake-reflection', 'Nature'),
    'Fondo2_16.png': ('Cozy Library Nook', 'whisperingsea4-cozy-library-nook', 'Cozy, Art'),
    'Fondo2_17.png': ('Dense Evergreen Forest', 'whisperingsea4-dense-evergreen-forest', 'Nature'),
    'Fondo2_18.png': ('Celestial Sun & Stars', 'whisperingsea4-celestial-sun-stars', 'Abstract, Fantasy'),
    'Fondo2_19.png': ('Atmospheric Cloud Horizons', 'whisperingsea4-atmospheric-cloud-horizons', 'Nature, Minimalist'),
    'Fondo2_20.png': ('Minimalist Frame Border Overlay', 'whisperingsea4-minimalist-frame-border', 'Minimalist, Transparent'),
    'Fondo2_21.png': ('Starlit Mountain Peak', 'whisperingsea4-starlit-mountain-peak', 'Nature, Sci-Fi'),
    'Fondo2_22.png': ('Ink Wash Pine Woods', 'whisperingsea4-ink-wash-pine-woods', 'Art, Nature'),
    'Fondo2_23.png': ('Moonlit Ocean Horizon', 'whisperingsea4-moonlit-ocean-horizon', 'Nature, Minimalist'),
    'Fondo2_24.png': ('Abstract Wave Ribbons', 'whisperingsea4-abstract-wave-ribbons', 'Abstract'),
    'Fondo2_25.png': ('High Detail Wilderness', 'whisperingsea4-high-detail-wilderness', 'Nature'),
    'Fondo2_26.png': ('Minimalist Crescent Moon', 'whisperingsea4-minimalist-crescent-moon', 'Minimalist'),
    'Fondo2_27.png': ('Bamboo Forest Sunlight', 'whisperingsea4-bamboo-forest-sunlight', 'Nature'),
    'Fondo2_28.png': ('Botanical Leaf Silhouette', 'whisperingsea4-botanical-leaf-silhouette', 'Nature, Minimalist'),
    'Fondo2_29.png': ('Atmospheric Mountain Fog', 'whisperingsea4-atmospheric-mountain-fog', 'Nature'),
    'Fondo2_30.png': ('Starry Night Valley Vista', 'whisperingsea4-starry-night-valley-vista', 'Nature, Fantasy'),
    'Fondo2_31.png': ('Mountain Sunset Outline', 'whisperingsea4-mountain-sunset-outline', 'Nature, Minimalist'),
    'Fondo2_32.png': ('Ink Line Pine Tree Overlay', 'whisperingsea4-dark-woodland-trail', 'Nature, Transparent'),
    'Fondo2_33.png': ('Minimalist Desert Cactus', 'whisperingsea4-minimalist-desert-cactus', 'Minimalist, Nature'),
    'Fondo2_34.png': ('Ink Splash Waves', 'whisperingsea4-ink-splash-waves', 'Art, Nature'),
    'Fondo2_35.png': ('Cozy Coffee & Reading', 'whisperingsea4-cozy-coffee-reading', 'Cozy, Minimalist'),
    'Fondo2_36.png': ('Japanese Torii Gate', 'whisperingsea4-japanese-torii-gate', 'Architecture, Art'),
    'Fondo2_37.png': ('Forest Under Stars', 'whisperingsea4-forest-under-stars', 'Nature, Fantasy'),
    'Fondo2_38.png': ('Geometric Mountain Sun', 'whisperingsea4-geometric-mountain-sun', 'Minimalist, Nature'),
    'Fondo2_39.png': ('Misty Pine Forest Path', 'whisperingsea4-misty-pine-forest-path', 'Nature'),
    'Fondo2_40.png': ('Minimalist Star Lines', 'whisperingsea4-minimalist-star-lines', 'Minimalist, Sci-Fi'),
    'Fondo2_41.png': ('Celestial Moon Phase', 'whisperingsea4-celestial-moon-phase', 'Abstract, Sci-Fi'),
    'Fondo2_42.png': ('Quiet Lake Reflection', 'whisperingsea4-quiet-lake-reflection', 'Nature, Minimalist'),
    'Fondo2_43.png': ('Starlight Mountain Vista', 'whisperingsea4-starlight-mountain-vista', 'Nature, Fantasy'),
    'Fondo2_2_-02.png': ('High Resolution Landscape II-A', 'whisperingsea4-highres-landscape-2a', 'Nature'),
    'Fondo2_2_-03.png': ('High Resolution Landscape II-B', 'whisperingsea4-highres-landscape-2b', 'Nature'),
    'Fondo2_2_-04.png': ('High Resolution Landscape II-C', 'whisperingsea4-highres-landscape-2c', 'Nature'),
    'Fondo2_2__Mesa de trabajo 1.png': ('High Resolution Master Canvas', 'whisperingsea4-highres-master-canvas', 'Art, Nature')
}

files = sorted(os.listdir(SRC_DIR))
candidates = []
for idx, filename in enumerate(files, start=1):
    info = title_map.get(filename, (f'WhisperingSea4 Screensaver {idx:02d}', f'whisperingsea4-item-{idx:02d}', 'r/koreader'))
    candidates.append({
        'id': info[1],
        'title': info[0],
        'author': 'u/WhisperingSea4',
        'authorUrl': 'https://reddit.com/r/koreader/comments/1kcsl0n/i_really_appreciate_the_screensavers_that/',
        'category': info[2],
        'sourceUrl': 'https://reddit.com/r/koreader/comments/1kcsl0n/i_really_appreciate_the_screensavers_that/',
        'license': 'Community Share',
        'licenseUrl': 'https://reddit.com/r/koreader/comments/1kcsl0n/i_really_appreciate_the_screensavers_that/',
        'attribution': 'r/koreader Community',
        'imageUrl': os.path.join(SRC_DIR, filename),
        'previewPath': f'review_thumbs_whisperingsea4/wss4-{idx:02d}.jpg'
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
    .card img { 
      width: 100%; 
      aspect-ratio: 3/4; 
      object-fit: contain; 
      display: block; 
      /* Checkerboard background for transparent overlays */
      background-color: #ffffff;
      background-image:  repeating-linear-gradient(45deg, #e2e8f0 25%, transparent 25%, transparent 75%, #e2e8f0 75%, #e2e8f0), repeating-linear-gradient(45deg, #e2e8f0 25%, #ffffff 25%, #ffffff 75%, #e2e8f0 75%, #e2e8f0);
      background-position: 0 0, 10px 10px;
      background-size: 20px 20px;
    }
    .card-body { padding: 12px; flex: 1; display: flex; flex-direction: column; gap: 6px; }
    .card-title { font-size: 0.95rem; font-weight: 600; color: #f1f5f9; margin: 0; word-break: break-word; }
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

print('Updated candidates_whisperingsea4.json and review_whisperingsea4.html with descriptive titles & checkerboard background!')
