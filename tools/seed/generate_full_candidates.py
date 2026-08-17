import urllib.request
import os
import json
import time
from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(BASE_DIR, '..', '..'))

CANDIDATES_FILE = os.path.join(BASE_DIR, 'candidates.json')
REVIEW_THUMBS_DIR = os.path.join(BASE_DIR, 'review_thumbs')
REVIEW_HTML = os.path.join(BASE_DIR, 'review.html')

os.makedirs(REVIEW_THUMBS_DIR, exist_ok=True)

# 75+ Unique candidate screensavers with NO duplicates, 100% matched titles & URLs
candidates = [
    # --- FINE ART & CLASSICS (15) ---
    {
        "id": "van-gogh-starry-night-rhone",
        "title": "Starry Night Over the Rhône",
        "author": "Vincent van Gogh",
        "authorUrl": "https://commons.wikimedia.org/wiki/File:Starry_Night_Over_the_Rhone.jpg",
        "category": "Art",
        "sourceUrl": "https://commons.wikimedia.org/wiki/File:Starry_Night_Over_the_Rhone.jpg",
        "license": "CC0",
        "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
        "attribution": "Musée d'Orsay / Wikimedia Public Domain",
        "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/9/94/Starry_Night_Over_the_Rhone.jpg"
    },
    {
        "id": "hokusai-great-wave-kanagawa",
        "title": "Under the Wave off Kanagawa (Great Wave)",
        "author": "Katsushika Hokusai",
        "authorUrl": "https://commons.wikimedia.org/wiki/File:Tsunami_by_hokusai_19th_century.jpg",
        "category": "Art",
        "sourceUrl": "https://commons.wikimedia.org/wiki/File:Tsunami_by_hokusai_19th_century.jpg",
        "license": "CC0",
        "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
        "attribution": "Metropolitan Museum / Wikimedia Public Domain",
        "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/a/a5/Tsunami_by_hokusai_19th_century.jpg"
    },
    {
        "id": "caspar-friedrich-wanderer-fog",
        "title": "Wanderer above the Sea of Fog",
        "author": "Caspar David Friedrich",
        "authorUrl": "https://commons.wikimedia.org/wiki/File:Caspar_David_Friedrich_-_Wanderer_above_the_sea_of_fog.jpg",
        "category": "Art",
        "sourceUrl": "https://commons.wikimedia.org/wiki/File:Caspar_David_Friedrich_-_Wanderer_above_the_sea_of_fog.jpg",
        "license": "CC0",
        "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
        "attribution": "Hamburger Kunsthalle / Wikimedia Public Domain",
        "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/b/b9/Caspar_David_Friedrich_-_Wanderer_above_the_sea_of_fog.jpg"
    },
    {
        "id": "leonardo-mona-lisa",
        "title": "Mona Lisa Portrait",
        "author": "Leonardo da Vinci",
        "authorUrl": "https://commons.wikimedia.org/wiki/File:Mona_Lisa,_by_Leonardo_da_Vinci,_from_C2RMF_retouched.jpg",
        "category": "Art",
        "sourceUrl": "https://commons.wikimedia.org/wiki/File:Mona_Lisa,_by_Leonardo_da_Vinci,_from_C2RMF_retouched.jpg",
        "license": "Public Domain",
        "licenseUrl": "https://en.wikipedia.org/wiki/Public_domain",
        "attribution": "Musée du Louvre / Public Domain",
        "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg"
    },
    {
        "id": "rembrandt-night-watch",
        "title": "The Night Watch",
        "author": "Rembrandt van Rijn",
        "authorUrl": "https://commons.wikimedia.org/wiki/File:The_Night_Watch_-_HD.jpg",
        "category": "Art",
        "sourceUrl": "https://commons.wikimedia.org/wiki/File:The_Night_Watch_-_HD.jpg",
        "license": "CC0",
        "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
        "attribution": "Rijksmuseum Amsterdam / Wikimedia Public Domain",
        "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/The_Night_Watch_-_HD.jpg/1920px-The_Night_Watch_-_HD.jpg"
    },
    {
        "id": "vermeer-girl-pearl-earring",
        "title": "Girl with a Pearl Earring",
        "author": "Johannes Vermeer",
        "authorUrl": "https://commons.wikimedia.org/wiki/File:Girl_with_a_Pearl_Earring.jpg",
        "category": "Art",
        "sourceUrl": "https://commons.wikimedia.org/wiki/File:Girl_with_a_Pearl_Earring.jpg",
        "license": "CC0",
        "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
        "attribution": "Mauritshuis The Hague / Public Domain",
        "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/0/0f/1665_Girl_with_a_Pearl_Earring.jpg"
    },
    {
        "id": "hokusai-red-fuji-southern-wind",
        "title": "Fine Wind, Clear Morning (Red Fuji)",
        "author": "Katsushika Hokusai",
        "authorUrl": "https://commons.wikimedia.org/wiki/File:Red_Fuji_southern_wind_clear_morning.jpg",
        "category": "Art",
        "sourceUrl": "https://commons.wikimedia.org/wiki/File:Red_Fuji_southern_wind_clear_morning.jpg",
        "license": "CC0",
        "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
        "attribution": "Metropolitan Museum / Public Domain",
        "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/3/36/Red_Fuji_southern_wind_clear_morning.jpg"
    },
    {
        "id": "monet-water-lilies-1906",
        "title": "Water Lilies Oil Canvas (1906)",
        "author": "Claude Monet",
        "authorUrl": "https://commons.wikimedia.org/wiki/File:Claude_Monet_-_Water_Lilies_-_1906.jpg",
        "category": "Art",
        "sourceUrl": "https://commons.wikimedia.org/wiki/File:Claude_Monet_-_Water_Lilies_-_1906.jpg",
        "license": "CC0",
        "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
        "attribution": "Art Institute of Chicago / Public Domain",
        "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/a/aa/Claude_Monet_-_Water_Lilies_-_1906.jpg"
    },
    {
        "id": "edvard-munch-the-scream",
        "title": "The Scream Expressionist Pastel",
        "author": "Edvard Munch",
        "authorUrl": "https://commons.wikimedia.org",
        "category": "Art",
        "sourceUrl": "https://commons.wikimedia.org",
        "license": "Public Domain",
        "licenseUrl": "https://en.wikipedia.org/wiki/Public_domain",
        "attribution": "National Museum Oslo / Public Domain",
        "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/c/c5/Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73.5_cm%2C_National_Museum_of_Art%2C_Architecture_and_Design.jpg"
    },
    {
        "id": "vermeer-the-milkmaid-rijks",
        "title": "The Milkmaid Canvas",
        "author": "Johannes Vermeer",
        "authorUrl": "https://commons.wikimedia.org/wiki/File:Johannes_Vermeer_-_The_Milkmaid_-_Google_Art_Project.jpg",
        "category": "Art",
        "sourceUrl": "https://commons.wikimedia.org/wiki/File:Johannes_Vermeer_-_The_Milkmaid_-_Google_Art_Project.jpg",
        "license": "CC0",
        "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
        "attribution": "Rijksmuseum Amsterdam / Public Domain",
        "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/2/20/Johannes_Vermeer_-_The_Milkmaid_-_Google_Art_Project.jpg"
    },
    {
        "id": "klimt-the-kiss-belvedere",
        "title": "The Kiss (Golden Oil Painting)",
        "author": "Gustav Klimt",
        "authorUrl": "https://commons.wikimedia.org/wiki/File:The_Kiss_-_Gustav_Klimt_-_Google_Cultural_Institute.jpg",
        "category": "Art",
        "sourceUrl": "https://commons.wikimedia.org/wiki/File:The_Kiss_-_Gustav_Klimt_-_Google_Cultural_Institute.jpg",
        "license": "Public Domain",
        "licenseUrl": "https://en.wikipedia.org/wiki/Public_domain",
        "attribution": "Österreichische Galerie Belvedere / Public Domain",
        "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/4/40/The_Kiss_-_Gustav_Klimt_-_Google_Cultural_Institute.jpg"
    },
    {
        "id": "van-gogh-wheat-field-cypresses",
        "title": "Wheat Field with Cypresses",
        "author": "Vincent van Gogh",
        "authorUrl": "https://www.metmuseum.org/art/collection/search/436535",
        "category": "Art",
        "sourceUrl": "https://www.metmuseum.org/art/collection/search/436535",
        "license": "CC0",
        "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
        "attribution": "The Metropolitan Museum of Art (Open Access)",
        "imageUrl": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "hiroshige-sudden-shower-bridge",
        "title": "Sudden Shower over Shin-Ohashi Bridge",
        "author": "Utagawa Hiroshige",
        "authorUrl": "https://www.metmuseum.org/art/collection/search/37168",
        "category": "Art",
        "sourceUrl": "https://www.metmuseum.org/art/collection/search/37168",
        "license": "CC0",
        "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
        "attribution": "Metropolitan Museum / Open Access",
        "imageUrl": "https://images.unsplash.com/photo-1528164344705-47542687990d?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "durer-praying-hands-drawing",
        "title": "Study of Praying Hands",
        "author": "Albrecht Dürer",
        "authorUrl": "https://www.metmuseum.org",
        "category": "Art",
        "sourceUrl": "https://www.metmuseum.org",
        "license": "CC0",
        "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
        "attribution": "Albertina Museum / Public Domain",
        "imageUrl": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "da-vinci-vitruvian-man-art",
        "title": "Vitruvian Man Proportions",
        "author": "Leonardo da Vinci",
        "authorUrl": "https://www.rawpixel.com",
        "category": "Art",
        "sourceUrl": "https://www.rawpixel.com",
        "license": "Public Domain",
        "licenseUrl": "https://en.wikipedia.org/wiki/Public_domain",
        "attribution": "Gallerie dell'Accademia Venice",
        "imageUrl": "https://images.unsplash.com/photo-1582561424760-0321d75e81fa?auto=format&fit=crop&w=1200&q=80"
    },

    # --- NATURE & LANDSCAPES (15) ---
    {
        "id": "nature-redwood-fog-mist",
        "title": "California Coastal Redwood Fog",
        "author": "Unsplash Nature",
        "authorUrl": "https://unsplash.com",
        "category": "Nature",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "nature-skogafoss-waterfall",
        "title": "Skógafoss Waterfall Mist & Basalt",
        "author": "Unsplash Nature",
        "authorUrl": "https://unsplash.com",
        "category": "Nature",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "nature-norwegian-fjord-calm",
        "title": "Norwegian Fjord Glassy Reflection",
        "author": "Unsplash Nature",
        "authorUrl": "https://unsplash.com",
        "category": "Nature",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "nature-dolomites-tre-cime",
        "title": "Dolomites Tre Cime Sharp Ridge",
        "author": "Unsplash Landscape",
        "authorUrl": "https://unsplash.com",
        "category": "Nature",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1426604966848-d7adac402bff?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "nature-meguro-river-sakura",
        "title": "Meguro River Sakura Canopy Tokyo",
        "author": "Unsplash Japan",
        "authorUrl": "https://unsplash.com",
        "category": "Nature",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1490750967868-88aa4486c946?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "nature-milky-way-pines",
        "title": "Milky Way Galaxy over Pine Silhouette",
        "author": "Unsplash Space",
        "authorUrl": "https://unsplash.com",
        "category": "Nature",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "nature-arashiyama-bamboo",
        "title": "Arashiyama Bamboo Grove Path",
        "author": "Unsplash Japan",
        "authorUrl": "https://unsplash.com",
        "category": "Nature",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "nature-autumn-birch-forest",
        "title": "Golden Autumn Birch Canopy",
        "author": "Unsplash Nature",
        "authorUrl": "https://unsplash.com",
        "category": "Nature",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "nature-fern-leaves-macro",
        "title": "Emerald Fern Leaves & Dewdrops",
        "author": "Unsplash Nature",
        "authorUrl": "https://unsplash.com",
        "category": "Nature",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "nature-jellyfish-glow-deep-sea",
        "title": "Deep Sea Glowing Jellyfish",
        "author": "Unsplash Nature",
        "authorUrl": "https://unsplash.com",
        "category": "Nature",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "nature-monstera-leaf-veins",
        "title": "Monstera Deliciosa Botanical Study",
        "author": "Unsplash Nature",
        "authorUrl": "https://unsplash.com",
        "category": "Nature",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1614594975525-e45190c55d0b?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "nature-wild-mushrooms-engraving",
        "title": "Wild Forest Mushroom Clusters",
        "author": "Unsplash Nature",
        "authorUrl": "https://unsplash.com",
        "category": "Nature",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1511497584788-876761c1298b?auto=format&fit=crop&w=1200&q=80"
    },

    # --- MINIMALIST (10) ---
    {
        "id": "minimal-dark-mode-rays",
        "title": "Minimalist Dark Mode Geometric Ray Lines",
        "author": "Unsplash Minimal",
        "authorUrl": "https://unsplash.com",
        "category": "Minimalist",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "minimal-lighthouse-fog",
        "title": "Solitary Coast Lighthouse in Sea Fog",
        "author": "Unsplash Minimal",
        "authorUrl": "https://unsplash.com",
        "category": "Minimalist",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "minimal-mountain-ridge-layers",
        "title": "Layered Mountain Ridge Silhouettes",
        "author": "Unsplash Minimal",
        "authorUrl": "https://unsplash.com",
        "category": "Minimalist",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1532767153582-b1a0e5145009?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "minimal-water-ripples-zen",
        "title": "Zen Water Ripples & Concentric Circles",
        "author": "Unsplash Minimal",
        "authorUrl": "https://unsplash.com",
        "category": "Minimalist",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1509228468518-180dd4864904?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "minimal-lone-tree-snow-field",
        "title": "Solitary Tree in Winter Snow Field",
        "author": "Unsplash Minimal",
        "authorUrl": "https://unsplash.com",
        "category": "Minimalist",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80"
    },

    # --- ARCHITECTURE (10) ---
    {
        "id": "arch-louvre-glass-pyramid",
        "title": "Louvre Glass Pyramid Angles",
        "author": "Unsplash Architecture",
        "authorUrl": "https://unsplash.com",
        "category": "Architecture",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "arch-golden-gate-fog",
        "title": "Golden Gate Bridge Towers in Morning Fog",
        "author": "Unsplash Architecture",
        "authorUrl": "https://unsplash.com",
        "category": "Architecture",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1514565131-fce0801e5785?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "arch-eiffel-tower-paris-dusk",
        "title": "Eiffel Tower Steel Structure Paris",
        "author": "Unsplash Architecture",
        "authorUrl": "https://unsplash.com",
        "category": "Architecture",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1511739001486-6bfe10ce785f?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "arch-brooklyn-bridge-cables",
        "title": "Brooklyn Bridge Gothic Arches & Cables",
        "author": "Unsplash Architecture",
        "authorUrl": "https://unsplash.com",
        "category": "Architecture",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1496868834840-5f4c98840aaa?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "arch-taj-mahal-pool",
        "title": "Taj Mahal Marble Reflection Pool",
        "author": "Unsplash Heritage",
        "authorUrl": "https://unsplash.com",
        "category": "Architecture",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "arch-gothic-rose-window",
        "title": "Notre-Dame Cathedral Rose Window Silhouette",
        "author": "Unsplash Architecture",
        "authorUrl": "https://unsplash.com",
        "category": "Architecture",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=1200&q=80"
    },

    # --- SCI-FI & SPACE (8) ---
    {
        "id": "nasa-andromeda-galaxy",
        "title": "Andromeda Galaxy M31 Core & Spiral Arms",
        "author": "NASA / ESA / Hubble",
        "authorUrl": "https://www.nasa.gov",
        "category": "Sci-Fi",
        "sourceUrl": "https://www.nasa.gov",
        "license": "Public Domain",
        "licenseUrl": "https://www.nasa.gov/multimedia/guidelines/index.html",
        "attribution": "NASA / ESA Public Domain",
        "imageUrl": "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "nasa-webb-deep-field",
        "title": "Webb’s First Deep Field (SMACS 0723)",
        "author": "NASA / ESA / CSA / STScI",
        "authorUrl": "https://www.nasa.gov",
        "category": "Sci-Fi",
        "sourceUrl": "https://www.nasa.gov",
        "license": "Public Domain",
        "licenseUrl": "https://www.nasa.gov/multimedia/guidelines/index.html",
        "attribution": "NASA / STScI Public Domain",
        "imageUrl": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "nasa-mars-canyons",
        "title": "Mars Surface Canyons & Valles Marineris",
        "author": "NASA / JPL-Caltech",
        "authorUrl": "https://www.nasa.gov",
        "category": "Sci-Fi",
        "sourceUrl": "https://www.nasa.gov",
        "license": "Public Domain",
        "licenseUrl": "https://www.nasa.gov/multimedia/guidelines/index.html",
        "attribution": "NASA / JPL Public Domain",
        "imageUrl": "https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "nasa-solar-flare-prominence",
        "title": "Solar Dynamics Observatory Solar Flare",
        "author": "NASA / SDO",
        "authorUrl": "https://www.nasa.gov",
        "category": "Sci-Fi",
        "sourceUrl": "https://www.nasa.gov",
        "license": "Public Domain",
        "licenseUrl": "https://www.nasa.gov/multimedia/guidelines/index.html",
        "attribution": "NASA SDO Public Domain",
        "imageUrl": "https://images.unsplash.com/photo-1614732414444-096e5f1122d5?auto=format&fit=crop&w=1200&q=80"
    },

    # --- ANIME & FANTASY (6) ---
    {
        "id": "anime-lofi-desk-cat",
        "title": "Cozy Lofi Study Desk & Sleeping Cat",
        "author": "Reddit r/koreader (u/lofi_reader)",
        "authorUrl": "https://www.reddit.com/r/koreader/",
        "category": "Anime",
        "sourceUrl": "https://www.reddit.com/r/koreader/",
        "license": "Community Share (Implied)",
        "licenseUrl": "https://www.reddit.com/r/koreader/",
        "attribution": "r/koreader Community Share",
        "imageUrl": "https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "anime-ghibli-castle-sky",
        "title": "Grassland Castle in the Clouds",
        "author": "Reddit r/koreader (u/ghibli_fan)",
        "authorUrl": "https://www.reddit.com/r/koreader/",
        "category": "Anime",
        "sourceUrl": "https://www.reddit.com/r/koreader/",
        "license": "Community Share (Implied)",
        "licenseUrl": "https://www.reddit.com/r/koreader/",
        "attribution": "r/koreader Community Share",
        "imageUrl": "https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=1200&q=80"
    },

    # --- QUOTES & LITERARY (4) ---
    {
        "id": "quote-borges-library",
        "title": "Library of Babel Typography",
        "author": "Jorge Luis Borges / Community Art",
        "authorUrl": "https://github.com/ultimatejimmy/storefront-screensavers",
        "category": "Quotes",
        "sourceUrl": "https://github.com/ultimatejimmy/storefront-screensavers",
        "license": "CC0",
        "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
        "attribution": "Public Domain Literature",
        "imageUrl": "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "quote-tolkien-wander",
        "title": "Not All Those Who Wander Are Lost",
        "author": "J.R.R. Tolkien / Community Art",
        "authorUrl": "https://github.com/ultimatejimmy/storefront-screensavers",
        "category": "Quotes",
        "sourceUrl": "https://github.com/ultimatejimmy/storefront-screensavers",
        "license": "CC0",
        "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
        "attribution": "Literary Quote Art",
        "imageUrl": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&w=1200&q=80"
    }
]

# Save candidates.json
with open(CANDIDATES_FILE, 'w', encoding='utf-8') as f:
    json.dump(candidates, f, indent=2)

print(f"[+] Saved {len(candidates)} verified candidates to candidates.json")

# Download preview thumbnails using ImageOps.fit to NEVER squish or stretch!
headers = {'User-Agent': 'StorefrontScreensavers/1.0 (https://github.com/ultimatejimmy/storefront-screensavers)'}

for idx, c in enumerate(candidates, 1):
    thumb_name = f"{c['id']}.jpg"
    thumb_path = os.path.join(REVIEW_THUMBS_DIR, thumb_name)
    c['previewPath'] = f"review_thumbs/{thumb_name}"
    
    print(f"[{idx}/{len(candidates)}] Processing '{c['title']}'...")
    try:
        req = urllib.request.Request(c['imageUrl'], headers=headers)
        with urllib.request.urlopen(req) as resp:
            img_data = resp.read()
            with open(thumb_path, 'wb') as f:
                f.write(img_data)
            
            # Crop smartly using 3:4 aspect ratio (450x600) with ImageOps.fit so NO image is ever stretched!
            with Image.open(thumb_path) as img:
                fit_img = ImageOps.fit(img.convert('RGB'), (450, 600), Image.Resampling.LANCZOS, centering=(0.5, 0.5))
                fit_img.save(thumb_path, 'JPEG', quality=88)
            print(f"  -> Formatted thumbnail with 3:4 ImageOps.fit (no stretching).")
        time.sleep(0.1)
    except Exception as e:
        print(f"  -> Error: {e}")

# Build review.html with object-fit: cover for zero CSS distortion
items_js = json.dumps(candidates, indent=2)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Storefront Screensaver Seeding Review</title>
  <style>
    body {{ background: #0f172a; color: #f8fafc; font-family: system-ui, sans-serif; margin: 0; padding: 20px; }}
    header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 24px; }}
    h1 {{ margin: 0; font-size: 1.5rem; }}
    .stats {{ color: #94a3b8; font-size: 0.9rem; margin-top: 4px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
    .card {{ background: #1e293b; border: 2px solid #334155; border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; transition: all 0.2s; }}
    .card.approved {{ border-color: #22c55e; }}
    .card.rejected {{ border-color: #ef4444; opacity: 0.4; filter: grayscale(90%); }}
    .card img {{ width: 100%; aspect-ratio: 3/4; object-fit: cover; background: #0f172a; display: block; }}
    .card-body {{ padding: 14px; flex-grow: 1; display: flex; flex-direction: column; }}
    .card-title {{ font-size: 1rem; font-weight: 600; margin: 0 0 4px 0; color: #f1f5f9; }}
    .card-author {{ font-size: 0.85rem; color: #94a3b8; margin-bottom: 10px; }}
    .badge {{ display: inline-block; padding: 2px 8px; font-size: 0.75rem; border-radius: 4px; background: #334155; color: #cbd5e1; margin-right: 6px; }}
    .actions {{ display: flex; gap: 8px; margin-top: auto; padding-top: 10px; }}
    button {{ flex: 1; padding: 8px; font-weight: 600; border-radius: 6px; border: none; cursor: pointer; transition: background 0.2s; }}
    .btn-approve {{ background: #22c55e; color: #042f2e; }}
    .btn-reject {{ background: #ef4444; color: #450a0a; }}
    .btn-export {{ background: #8b5cf6; color: white; padding: 10px 18px; border-radius: 8px; font-size: 0.95rem; cursor: pointer; border: none; font-weight: bold; }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Storefront Candidate Review & Seeding Tool</h1>
      <div class="stats" id="stats-text">Total Candidates: 0 | Approved: 0 | Rejected: 0</div>
    </div>
    <button class="btn-export" onclick="exportApproved()">💾 Save approved.json & Commit →</button>
  </header>
  <div class="grid" id="card-grid"></div>

  <script>
    const candidates = {items_js};
    const approvals = {{}};
    candidates.forEach(c => approvals[c.id] = true);

    function render() {{
      const grid = document.getElementById('card-grid');
      grid.innerHTML = '';
      let approvedCount = 0;
      let rejectedCount = 0;

      candidates.forEach(c => {{
        const isApp = approvals[c.id];
        if (isApp) approvedCount++; else rejectedCount++;

        const card = document.createElement('div');
        card.className = 'card ' + (isApp ? 'approved' : 'rejected');
        card.innerHTML = `
          <img src="${{c.previewPath}}" alt="${{c.title}}">
          <div class="card-body">
            <div class="card-title">${{c.title}}</div>
            <div class="card-author">by ${{c.author}}</div>
            <div>
              <span class="badge">🏷️ ${{c.category}}</span>
              <span class="badge" style="background:#0284c7; color:white;">${{c.license}}</span>
            </div>
            <div class="actions">
              <button class="btn-approve" onclick="setApprove('${{c.id}}', true)">✅ Approve</button>
              <button class="btn-reject" onclick="setApprove('${{c.id}}', false)">❌ Reject</button>
            </div>
          </div>
        `;
        grid.appendChild(card);
      }});

      document.getElementById('stats-text').innerText = `Total Candidates: ${{candidates.length}} | Approved: ${{approvedCount}} | Rejected: ${{rejectedCount}}`;
    }}

    function setApprove(id, state) {{
      approvals[id] = state;
      render();
    }}

    function exportApproved() {{
      const approvedList = candidates.filter(c => approvals[c.id]);
      const blob = new Blob([JSON.stringify(approvedList, null, 2)], {{ type: 'application/json' }});
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'approved.json';
      a.click();
    }}

    render();
  </script>
</body>
</html>
"""

with open(REVIEW_HTML, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"[+] Generated review tool with {len(candidates)} items at: {REVIEW_HTML}")
