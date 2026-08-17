import os
import json
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(BASE_DIR, '..', '..'))
SCREENSAVERS_JSON = os.path.join(REPO_ROOT, 'screensavers.json')

with open(SCREENSAVERS_JSON, 'r', encoding='utf-8') as f:
    catalog = json.load(f)

print(f"[+] Enriching tags for {len(catalog)} screensavers...")

# Common stop words to ignore when generating tags from titles
STOP_WORDS = {
    'a', 'an', 'and', 'the', 'in', 'on', 'at', 'by', 'for', 'with', 'about', 'against',
    'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to',
    'from', 'up', 'down', 'of', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
    'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few',
    'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
    'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now',
    'i', 'ii', 'iii', 'iv', 'v', 'vi', '1', '2', '3', '4', '5', 'art', 'wallpaper', 'screensaver', 'image'
}

# Thematic keyword mapping dictionary
TOPIC_KEYWORDS = {
    'cat': ['cat', 'feline', 'kitten', 'pet', 'animal'],
    'dog': ['dog', 'canine', 'puppy', 'pet', 'animal'],
    'whale': ['whale', 'ocean', 'marine', 'sea', 'aquatic', 'wildlife'],
    'ocean': ['ocean', 'sea', 'waves', 'water', 'marine', 'coastal'],
    'mountain': ['mountain', 'peaks', 'summit', 'alpine', 'nature', 'landscape'],
    'forest': ['forest', 'woods', 'trees', 'nature', 'landscape'],
    'pine': ['pines', 'pine trees', 'evergreen', 'forest', 'nature'],
    'space': ['space', 'cosmos', 'galaxy', 'astronomy', 'stars', 'universe'],
    'stars': ['stars', 'night sky', 'constellations', 'astronomy'],
    'moon': ['moon', 'lunar', 'crescent', 'night', 'celestial'],
    'sun': ['sun', 'solar', 'sunlight', 'sunrise', 'sunset', 'daylight'],
    'cloud': ['clouds', 'sky', 'weather', 'atmospheric'],
    'fog': ['fog', 'mist', 'hazy', 'atmospheric', 'moody'],
    'rain': ['rain', 'rainy', 'weather', 'water', 'moody'],
    'tree': ['tree', 'nature', 'botanical', 'foliage'],
    'flower': ['flower', 'floral', 'botanical', 'bloom', 'plants'],
    'leaf': ['leaf', 'foliage', 'botanical', 'nature', 'plants'],
    'dragon': ['dragon', 'fantasy', 'creature', 'mythical'],
    'frieren': ['frieren', 'fern', 'anime', 'manga', 'fantasy', 'magic'],
    'spirited': ['spirited away', 'haku', 'ghibli', 'anime', 'miyazaki'],
    'garfield': ['garfield', 'comic', 'cartoon', 'cat', 'humor', 'reading'],
    'baymax': ['baymax', 'big hero 6', 'disney', 'robot', 'friendly'],
    'marvel': ['marvel', 'superheroes', 'comic', 'avengers'],
    'reading': ['reading', 'book', 'literature', 'library', 'cozy'],
    'coffee': ['coffee', 'cafe', 'cozy', 'warm', 'morning'],
    'library': ['library', 'books', 'literature', 'cozy', 'study'],
    'window': ['window', 'cozy', 'interior', 'view'],
    'castle': ['castle', 'medieval', 'architecture', 'fortress', 'historic'],
    'japan': ['japan', 'japanese', 'oriental', 'traditional', 'east asia'],
    'torii': ['torii', 'shrine', 'japan', 'japanese', 'architecture', 'gate'],
    'bamboo': ['bamboo', 'grove', 'forest', 'nature', 'japan', 'botanical'],
    'desert': ['desert', 'dunes', 'sand', 'arid', 'wilderness'],
    'cactus': ['cactus', 'desert', 'succulent', 'botanical', 'plants'],
    'minimalist': ['minimalist', 'clean', 'simple', 'monochrome', 'line art'],
    'geometric': ['geometric', 'geometry', 'shapes', 'abstract', 'patterns'],
    'retro': ['retro', 'vintage', 'classic', 'nostalgia'],
    'cyberpunk': ['cyberpunk', 'sci-fi', 'futuristic', 'neon', 'city'],
    'city': ['city', 'urban', 'architecture', 'buildings', 'skyline'],
    'lighthouse': ['lighthouse', 'coast', 'ocean', 'beacon', 'maritime'],
    'hokusai': ['hokusai', 'ukiyo-e', 'woodblock', 'japanese art', 'classic art'],
    'engraving': ['engraving', 'woodcut', 'etching', 'vintage', 'classic art', 'lithograph'],
    'drawing': ['drawing', 'sketch', 'illustration', 'line art', 'ink'],
    'mandala': ['mandala', 'pattern', 'meditation', 'sacred geometry', 'spiritual'],
    'transparent': ['transparent', 'overlay', 'koreader overlay', 'backdrop']
}

for item in catalog:
    existing_tags = item.get('tags', [])
    if isinstance(existing_tags, str):
        existing_tags = [t.strip().lower() for t in existing_tags.split(',') if t.strip()]
    elif isinstance(existing_tags, list):
        existing_tags = [str(t).strip().lower() for t in existing_tags if str(t).strip()]
    else:
        existing_tags = []

    tags_set = set(existing_tags)

    title = item.get('title', '')
    category = item.get('category', '')
    author = item.get('author', '')
    item_id = item.get('id', '')

    # 1. Add Category as tags
    if isinstance(category, list):
        for c in category:
            c_clean = str(c).strip().lower()
            if c_clean:
                tags_set.add(c_clean)
    elif isinstance(category, str) and category.strip():
        for c in category.split(','):
            c_clean = c.strip().lower()
            if c_clean:
                tags_set.add(c_clean)

    # 2. Extract meaningful title words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', title.lower())
    for w in words:
        if w not in STOP_WORDS:
            tags_set.add(w)

    # 3. Match topic keywords from title, author, and category
    full_text = f"{title} {category} {author} {item_id}".lower()
    for key, related in TOPIC_KEYWORDS.items():
        if key in full_text:
            for r in related:
                tags_set.add(r)

    # 4. Check if Transparent
    if 'transparent' in str(category).lower() or item_id.startswith('rb-') or 'overlay' in full_text:
        tags_set.add('transparent')
        tags_set.add('overlay')

    # Ensure clean sorted list of unique tags
    clean_tags = sorted(list(tags_set))
    item['tags'] = clean_tags

# Save updated catalog
with open(SCREENSAVERS_JSON, 'w', encoding='utf-8') as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"[+] Successfully seeded tags for all {len(catalog)} screensavers in screensavers.json!")
print("Sample tags from first 5 items:")
for item in catalog[:5]:
    print(f"  - {item['title']}: {item['tags']}")
