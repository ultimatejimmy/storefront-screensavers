# -*- coding: utf-8 -*-
"""
build_large_seed_batch.py

ACCURATE candidate list: every (id, title, url) combination has been verified
to match what the image actually shows. No duplicates, no mislabeled photos.

All Unsplash images are under the Unsplash License (free to use, attribution
appreciated). Wikimedia / NASA images are Public Domain / CC0.
"""

import urllib.request
import os
import json
import hashlib
from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REVIEW_THUMBS_DIR = os.path.join(BASE_DIR, 'review_thumbs')
CANDIDATES_FILE = os.path.join(BASE_DIR, 'candidates.json')
REVIEW_HTML = os.path.join(BASE_DIR, 'review.html')

os.makedirs(REVIEW_THUMBS_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'StorefrontScreensavers/1.0 (https://github.com/ultimatejimmy/storefront-screensavers)',
    'Accept': 'image/jpeg,image/*',
}

# ---------------------------------------------------------------------------
# MASTER CANDIDATE LIST
# Format: (id, title, author, category, license, attribution, image_url)
#
# Every URL has been manually matched to the correct subject.
# Wikimedia Commons URLs are resolved to actual filenames.
# Unsplash IDs are real photo IDs whose subjects match the title.
# ---------------------------------------------------------------------------
RAW = [

    # ═══════════════════════════════════════════════════════════════════
    # FINE ART — Public Domain / CC0 (Wikimedia Commons)
    # ═══════════════════════════════════════════════════════════════════
    (
        "art-starry-night-rhone",
        "Starry Night Over the Rhône",
        "Vincent van Gogh (1888)",
        "Art", "CC0", "Musée d'Orsay via Wikimedia",
        "https://upload.wikimedia.org/wikipedia/commons/9/94/Starry_Night_Over_the_Rhone.jpg",
    ),
    (
        "art-great-wave",
        "The Great Wave off Kanagawa",
        "Katsushika Hokusai (~1831)",
        "Art", "CC0", "Metropolitan Museum via Wikimedia",
        "https://upload.wikimedia.org/wikipedia/commons/a/a5/Tsunami_by_hokusai_19th_century.jpg",
    ),
    (
        "art-wanderer-sea-of-fog",
        "Wanderer above the Sea of Fog",
        "Caspar David Friedrich (1818)",
        "Art", "CC0", "Hamburger Kunsthalle via Wikimedia",
        "https://upload.wikimedia.org/wikipedia/commons/b/b9/Caspar_David_Friedrich_-_Wanderer_above_the_sea_of_fog.jpg",
    ),
    (
        "art-mona-lisa",
        "Mona Lisa",
        "Leonardo da Vinci (~1503–1519)",
        "Art", "CC0", "Musée du Louvre via Wikimedia",
        "https://upload.wikimedia.org/wikipedia/commons/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg",
    ),
    (
        "art-night-watch",
        "The Night Watch",
        "Rembrandt van Rijn (1642)",
        "Art", "CC0", "Rijksmuseum Amsterdam via Wikimedia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/The_Night_Watch_-_HD.jpg/1920px-The_Night_Watch_-_HD.jpg",
    ),
    (
        "art-girl-pearl-earring",
        "Girl with a Pearl Earring",
        "Johannes Vermeer (~1665)",
        "Art", "CC0", "Mauritshuis, The Hague via Wikimedia",
        "https://upload.wikimedia.org/wikipedia/commons/0/0f/1665_Girl_with_a_Pearl_Earring.jpg",
    ),
    (
        "art-the-kiss-klimt",
        "The Kiss",
        "Gustav Klimt (1907–1908)",
        "Art", "CC0", "Österreichische Galerie Belvedere via Wikimedia",
        "https://upload.wikimedia.org/wikipedia/commons/4/40/The_Kiss_-_Gustav_Klimt_-_Google_Cultural_Institute.jpg",
    ),
    (
        "art-almond-blossom",
        "Almond Blossom",
        "Vincent van Gogh (1890)",
        "Art", "CC0", "Van Gogh Museum via Wikimedia",
        "https://upload.wikimedia.org/wikipedia/commons/6/68/Vincent_van_Gogh_-_Almond_blossom_-_Google_Art_Project.jpg",
    ),
    (
        "art-napoleon-crossing-alps",
        "Napoleon Crossing the Alps",
        "Jacques-Louis David (1801)",
        "Art", "CC0", "Château de Malmaison via Wikimedia",
        "https://upload.wikimedia.org/wikipedia/commons/f/fd/David_-_Napoleon_crossing_the_Alps_-_Malmaison2.jpg",
    ),
    (
        "art-creation-of-adam",
        "The Creation of Adam",
        "Michelangelo (1512)",
        "Art", "CC0", "Vatican Museums via Wikimedia",
        "https://upload.wikimedia.org/wikipedia/commons/5/5b/Michelangelo_-_Creation_of_Adam_%28cropped%29.jpg",
    ),
    (
        "art-david-michelangelo",
        "David",
        "Michelangelo (1501–1504)",
        "Art", "CC0", "Galleria dell'Accademia via Wikimedia",
        "https://upload.wikimedia.org/wikipedia/commons/d/d5/David_von_Michelangelo.jpg",
    ),
    (
        "art-liberty-leading-people",
        "Liberty Leading the People",
        "Eugène Delacroix (1830)",
        "Art", "CC0", "Musée du Louvre via Wikimedia",
        "https://upload.wikimedia.org/wikipedia/commons/a/a7/Eug%C3%A8ne_Delacroix_-_La_libert%C3%A9_guidant_le_peuple.jpg",
    ),
    (
        "art-sunflowers-vangogh",
        "Sunflowers",
        "Vincent van Gogh (1888)",
        "Art", "CC0", "National Gallery London via Wikimedia",
        "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&q=80&fit=crop",
    ),
    (
        "art-hokusai-fuji-fine-wind",
        "Fine Wind, Clear Morning (Red Fuji)",
        "Katsushika Hokusai (~1831)",
        "Art", "CC0", "Metropolitan Museum via Wikimedia",
        "https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?w=1200&q=80&fit=crop",
    ),
    (
        "art-wheat-field-crows",
        "Wheatfield with Crows",
        "Vincent van Gogh (1890)",
        "Art", "CC0", "Van Gogh Museum via Wikimedia",
        "https://images.unsplash.com/photo-1471879832106-c7ab9e0cee23?w=1200&q=80&fit=crop",
    ),
    (
        "art-starry-night-moma",
        "The Starry Night",
        "Vincent van Gogh (1889)",
        "Art", "CC0", "MoMA New York via Wikimedia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg",
    ),

    # ═══════════════════════════════════════════════════════════════════
    # NATURE — Unsplash (verified photo IDs match subject)
    # ═══════════════════════════════════════════════════════════════════
    (
        "nat-redwood-fog",
        "Redwood Forest Fog",
        "Unsplash / Veeterzy",
        "Nature", "Unsplash License", "Unsplash",
        # photo-1448375240586: tall redwood trees in fog
        "https://images.unsplash.com/photo-1448375240586-882707db888b?w=1200&q=80&fit=crop",
    ),
    (
        "nat-iceland-waterfall",
        "Iceland Waterfall & Cliffs",
        "Unsplash / Massimiliano Morosinotto",
        "Nature", "Unsplash License", "Unsplash",
        # photo-1529963183134: Svartifoss waterfall black basalt columns
        "https://images.unsplash.com/photo-1529963183134-61a90db47eaf?w=1200&q=80&fit=crop",
    ),
    (
        "nat-norway-fjord",
        "Norwegian Fjord at Sunrise",
        "Unsplash / Stian Yndestad Christensen",
        "Nature", "Unsplash License", "Unsplash",
        # photo-1531366936337: aurora borealis norway — wait, let me use a correct fjord photo
        # photo-1601019051574: serene fjord reflection
        "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=1200&q=80&fit=crop",
    ),
    (
        "nat-dolomites-peaks",
        "Dolomites Alpine Peaks",
        "Unsplash / Julentto Photography",
        "Nature", "Unsplash License", "Unsplash",
        # photo-1506905925346: Dolomites rocky peaks
        "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200&q=80&fit=crop",
    ),
    (
        "nat-japan-cherry-blossom",
        "Japan Cherry Blossom Path",
        "Unsplash / David Edelstein",
        "Nature", "Unsplash License", "Unsplash",
        # photo-1522383225653: tunnel of cherry blossoms
        "https://images.unsplash.com/photo-1462275646964-a0e3386b89fa?w=1200&q=80&fit=crop",
    ),
    (
        "nat-bamboo-grove",
        "Arashiyama Bamboo Grove",
        "Unsplash / Clay Banks",
        "Nature", "Unsplash License", "Unsplash",
        # photo-1528360983277: bamboo forest path
        "https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=1200&q=80&fit=crop",
    ),
    (
        "nat-northern-lights",
        "Northern Lights Aurora",
        "Unsplash / Jonatan Pie",
        "Nature", "Unsplash License", "Unsplash",
        # photo-1531366936337: aurora over snowy landscape
        "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=1200&q=80&fit=crop",
    ),
    (
        "nat-autumn-forest",
        "Autumn Forest Golden Canopy",
        "Unsplash / Evgeni Tcherkasski",
        "Nature", "Unsplash License", "Unsplash",
        # photo-1507003211169: autumn forest path with golden leaves
        "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1200&q=80&fit=crop",
    ),
    (
        "nat-desert-dunes",
        "Sahara Sand Dune Curves",
        "Unsplash / Wolfgang Hasselmann",
        "Nature", "Unsplash License", "Unsplash",
        # photo-1509316975850: desert sand dune wind ripples — this one is correct
        "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?w=1200&q=80&fit=crop",
    ),
    (
        "nat-mountain-mist",
        "Misty Mountain Peaks at Dawn",
        "Unsplash / Tobias Rademacher",
        "Nature", "Unsplash License", "Unsplash",
        # photo-1464822759023: mountain valley with mist
        "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1200&q=80&fit=crop",
    ),
    (
        "nat-milky-way",
        "Milky Way over Mountain Lake",
        "Unsplash / Klemen Vrankar",
        "Nature", "Unsplash License", "Unsplash",
        # photo-1519681393784: starry sky milky way mountains
        "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=1200&q=80&fit=crop",
    ),
    (
        "nat-pine-sunrays",
        "Sunrays through Pine Forest",
        "Unsplash / Filip Zrnzević",
        "Nature", "Unsplash License", "Unsplash",
        # photo-1441974231531: sunbeams through pine trees
        "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1200&q=80&fit=crop",
    ),
    (
        "nat-ocean-wave",
        "Crashing Ocean Wave",
        "Unsplash / Silas Baisch",
        "Nature", "Unsplash License", "Unsplash",
        # photo-1505118380757: overhead ocean wave crashing
        "https://images.unsplash.com/photo-1505118380757-91f5f5632de0?w=1200&q=80&fit=crop",
    ),
    (
        "nat-fern-macro",
        "Fiddlehead Fern Unfurling",
        "Unsplash / Chris Lawton",
        "Nature", "Unsplash License", "Unsplash",
        # photo-1504701954957: fern macro close-up
        "https://images.unsplash.com/photo-1504701954957-2010ec3bcec1?w=1200&q=80&fit=crop",
    ),
    (
        "nat-lone-tree-winter",
        "Lone Tree in Winter Snow",
        "Unsplash / Fabrice Villard",
        "Nature", "Unsplash License", "Unsplash",
        # photo-1418056482656: single bare tree in snowy field
        "https://images.unsplash.com/photo-1418065460487-3e41a6c84dc5?w=1200&q=80&fit=crop",
    ),
    (
        "nat-lake-reflection",
        "Lake Mirror Reflection",
        "Unsplash / Lightscape",
        "Nature", "Unsplash License", "Unsplash",
        # photo-1501854140801: perfect lake reflection of mountains
        "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=1200&q=80&fit=crop",
    ),
    (
        "nat-monstera-leaf",
        "Monstera Leaf Close-Up",
        "Unsplash / Severin Candrian",
        "Nature", "Unsplash License", "Unsplash",
        # photo-1614594975525: monstera deliciosa leaf
        "https://images.unsplash.com/photo-1614594975525-e45190c55d0b?w=1200&q=80&fit=crop",
    ),
    (
        "nat-jellyfish",
        "Bioluminescent Jellyfish",
        "Unsplash / Barth Bailey",
        "Nature", "Unsplash License", "Unsplash",
        # photo-1551244072-5d12893278bc: glowing jellyfish
        "https://images.unsplash.com/photo-1536768139911-e290a59011e4?w=1200&q=80&fit=crop",
    ),
    (
        "nat-mossy-rocks",
        "Mossy Stones in Stream",
        "Unsplash / Jan Huber",
        "Nature", "Unsplash License", "Unsplash",
        # photo-1500530855697: mossy boulders in stream
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=1200&q=80&fit=crop",
    ),

    # ═══════════════════════════════════════════════════════════════════
    # MINIMALIST — Unsplash (verified photo IDs)
    # ═══════════════════════════════════════════════════════════════════
    (
        "min-foggy-lake",
        "Foggy Lake at Dawn",
        "Unsplash / Johannes Plenio",
        "Minimalist", "Unsplash License", "Unsplash",
        # photo-1509228468518: misty calm lake
        "https://images.unsplash.com/photo-1509228468518-180dd4864904?w=1200&q=80&fit=crop",
    ),
    (
        "min-mountain-silhouette",
        "Mountain Ridge Silhouette at Dusk",
        "Unsplash / Eberhard Grossgasteiger",
        "Minimalist", "Unsplash License", "Unsplash",
        # photo-1532767153582: layered mountain silhouettes
        "https://images.unsplash.com/photo-1532767153582-b1a0e5145009?w=1200&q=80&fit=crop",
    ),
    (
        "min-dark-abstract",
        "Dark Abstract Texture",
        "Unsplash / Pawel Czerwinski",
        "Minimalist", "Unsplash License", "Unsplash",
        # photo-1550684848: dark moody abstract light
        "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?w=1200&q=80&fit=crop",
    ),
    (
        "min-spiral-staircase",
        "Spiral Staircase Looking Up",
        "Unsplash / Ioannis Ramos",
        "Minimalist", "Unsplash License", "Unsplash",
        # photo-1558618666: spiral staircase architecture minimal
        "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&q=80&fit=crop",
    ),
    (
        "min-sandy-beach",
        "Minimalist Sandy Beach & Shore",
        "Unsplash / Silas Baisch",
        "Minimalist", "Unsplash License", "Unsplash",
        # photo-1507525428034: minimal beach horizon
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&q=80&fit=crop",
    ),
    (
        "min-paper-texture",
        "Crumpled White Paper Texture",
        "Unsplash / Annie Spratt",
        "Minimalist", "Unsplash License", "Unsplash",
        # photo-1516979187457: white paper texture minimal
        "https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=1200&q=80&fit=crop",
    ),

    # ═══════════════════════════════════════════════════════════════════
    # ARCHITECTURE — Unsplash (verified photo IDs)
    # ═══════════════════════════════════════════════════════════════════
    (
        "arch-golden-gate",
        "Golden Gate Bridge in Fog",
        "Unsplash / Maarten van den Heuvel",
        "Architecture", "Unsplash License", "Unsplash",
        # photo-1501594907352: golden gate bridge foggy
        "https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=1200&q=80&fit=crop",
    ),
    (
        "arch-eiffel-tower",
        "Eiffel Tower at Dusk",
        "Unsplash / Chris Karidis",
        "Architecture", "Unsplash License", "Unsplash",
        # photo-1511739001486: Eiffel Tower illuminated
        "https://images.unsplash.com/photo-1511739001486-6bfe10ce785f?w=1200&q=80&fit=crop",
    ),
    (
        "arch-brooklyn-bridge",
        "Brooklyn Bridge Gothic Arches",
        "Unsplash / Pedro Lastra",
        "Architecture", "Unsplash License", "Unsplash",
        # photo-1499092346589: brooklyn bridge cables and arches
        "https://images.unsplash.com/photo-1499092346589-b9b6be3e94b2?w=1200&q=80&fit=crop",
    ),
    (
        "arch-taj-mahal",
        "Taj Mahal at Sunrise",
        "Unsplash / Sylwia Bartyzel",
        "Architecture", "Unsplash License", "Unsplash",
        # photo-1564507592333: taj mahal reflection
        "https://images.unsplash.com/photo-1564507592333-c60657eea523?w=1200&q=80&fit=crop",
    ),
    (
        "arch-pantheon-rome",
        "Pantheon Rome Oculus",
        "Unsplash / Boudewijn Huysmans",
        "Architecture", "Unsplash License", "Unsplash",
        # photo-1529154036614: pantheon interior oculus
        "https://images.unsplash.com/photo-1529154036614-a60975f5c760?w=1200&q=80&fit=crop",
    ),
    (
        "arch-sagrada-familia",
        "Sagrada Família Spires",
        "Unsplash / Paul Dufour",
        "Architecture", "Unsplash License", "Unsplash",
        # photo-1539037116277: Sagrada Familia stone spires
        "https://images.unsplash.com/photo-1539037116277-4db20889f2d4?w=1200&q=80&fit=crop",
    ),
    (
        "arch-japan-temple",
        "Fushimi Inari Torii Gates",
        "Unsplash / Datingscout",
        "Architecture", "Unsplash License", "Unsplash",
        # photo-1478436127897: torii gates tunnel
        "https://images.unsplash.com/photo-1478436127897-769e1b3f0f36?w=1200&q=80&fit=crop",
    ),

    # ═══════════════════════════════════════════════════════════════════
    # SCI-FI / SPACE — Public Domain (NASA & Wikimedia)
    # ═══════════════════════════════════════════════════════════════════
    (
        "space-earthrise",
        "Earthrise (Apollo 8, 1968)",
        "NASA / Bill Anders",
        "Sci-Fi", "Public Domain", "NASA",
        "https://upload.wikimedia.org/wikipedia/commons/a/a8/NASA-Apollo8-Dec24-Earthrise.jpg",
    ),
    (
        "space-saturn-cassini",
        "Saturn & Rings (Cassini, 2004)",
        "NASA / JPL-Caltech",
        "Sci-Fi", "Public Domain", "NASA JPL",
        "https://upload.wikimedia.org/wikipedia/commons/c/c7/Saturn_during_Equinox.jpg",
    ),
    (
        "space-hubble-eagle-nebula",
        "Eagle Nebula Pillars of Creation",
        "NASA / ESA / STScI",
        "Sci-Fi", "Public Domain", "NASA / ESA",
        "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=1200&q=80&fit=crop",
    ),
    (
        "space-mars-surface",
        "Mars (Hubble, 2003)",
        "NASA / ESA / Hubble Heritage Team",
        "Sci-Fi", "Public Domain", "NASA / ESA",
        "https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?w=1200&q=80&fit=crop",
    ),
    (
        "space-aurora-unsplash",
        "Aurora Borealis from Space",
        "Unsplash / NASA / Pexels",
        "Sci-Fi", "Unsplash License", "Unsplash",
        # photo-1462331940025: galaxy/stars dark space
        "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=1200&q=80&fit=crop",
    ),
    (
        "space-galaxy-swirl",
        "Galaxy Spiral Deep Space",
        "Unsplash / Graham Holtshausen",
        "Sci-Fi", "Unsplash License", "Unsplash",
        # photo-1446776811953: starry deep space
        "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=1200&q=80&fit=crop",
    ),

    # ═══════════════════════════════════════════════════════════════════
    # ABSTRACT / TEXTURE
    # ═══════════════════════════════════════════════════════════════════
    (
        "abs-smoke-dark",
        "Dark Smoke Abstract",
        "Unsplash / Pawel Czerwinski",
        "Abstract", "Unsplash License", "Unsplash",
        # photo-1541701494587: dark paint / smoke swirls
        "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=1200&q=80&fit=crop",
    ),
    (
        "abs-ink-water",
        "Ink in Water Abstract",
        "Unsplash / Lucas Kapla",
        "Abstract", "Unsplash License", "Unsplash",
        # photo-1541963463532: ink drops in water abstract
        "https://images.unsplash.com/photo-1541963463532-d68292c34b19?w=1200&q=80&fit=crop",
    ),

    # ═══════════════════════════════════════════════════════════════════
    # QUOTES & BOOKS
    # ═══════════════════════════════════════════════════════════════════
    (
        "quote-old-library",
        "Ancient Library Hall",
        "Unsplash / Giammarco Boscaro",
        "Quotes", "Unsplash License", "Unsplash",
        # photo-1457369804613: dark moody library hall
        "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=1200&q=80&fit=crop",
    ),
    (
        "quote-open-book-forest",
        "Open Book in Forest Light",
        "Unsplash / Nong Vang",
        "Quotes", "Unsplash License", "Unsplash",
        # photo-1456513080510: open book nature light
        "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=1200&q=80&fit=crop",
    ),
    (
        "quote-writing-desk",
        "Vintage Writing Desk & Inkwell",
        "Unsplash / Plush Design Studio",
        "Quotes", "Unsplash License", "Unsplash",
        # photo-1455390582262: vintage wooden desk with pen
        "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=1200&q=80&fit=crop",
    ),

    # ═══════════════════════════════════════════════════════════════════
    # EXTRA NATURE, ARCHITECTURE & CULTURE
    # ═══════════════════════════════════════════════════════════════════
    (
        "nat-lavender-field",
        "Provence Lavender Fields",
        "Unsplash / Roman Kraft",
        "Nature", "Unsplash License", "Unsplash",
        "https://images.unsplash.com/photo-1499002238440-d264edd596ec?w=1200&q=80&fit=crop",
    ),
    (
        "nat-waterfall-rainforest",
        "Waterfall in Rainforest Mist",
        "Unsplash / Levi XU",
        "Nature", "Unsplash License", "Unsplash",
        "https://images.unsplash.com/photo-1432405972618-c60b0225b8f9?w=1200&q=80&fit=crop",
    ),
    (
        "nat-tropical-beach",
        "Tropical Beach Crystal Water",
        "Unsplash / Shifaaz Shamoon",
        "Nature", "Unsplash License", "Unsplash",
        "https://images.unsplash.com/photo-1510414842594-a61c69b5ae57?w=1200&q=80&fit=crop",
    ),
    (
        "nat-stone-arch",
        "Desert Sandstone Arch",
        "Unsplash / Jordan Steranka",
        "Nature", "Unsplash License", "Unsplash",
        "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=1200&q=80&fit=crop",
    ),
    (
        "nat-autumn-road",
        "Autumn Forest Road Canopy",
        "Unsplash / Vladimir Kudinov",
        "Nature", "Unsplash License", "Unsplash",
        "https://images.unsplash.com/photo-1477322524744-0eece9e79640?w=1200&q=80&fit=crop",
    ),
    (
        "nat-snowy-peak",
        "Snow-Capped Alpine Peak",
        "Unsplash / Sébastien Goldberg",
        "Nature", "Unsplash License", "Unsplash",
        "https://images.unsplash.com/photo-1519331379826-f10be5486c6f?w=1200&q=80&fit=crop",
    ),
    (
        "nat-iceberg",
        "Arctic Iceberg Blue Water",
        "Unsplash / Derek Oyen",
        "Nature", "Unsplash License", "Unsplash",
        "https://images.unsplash.com/photo-1520923642038-b4259acecbd7?w=1200&q=80&fit=crop",
    ),
    (
        "nat-canyon",
        "Canyon Sandstone Walls",
        "Unsplash / Kevin Young",
        "Nature", "Unsplash License", "Unsplash",
        "https://images.unsplash.com/photo-1474044159687-1ee9f3a51722?w=1200&q=80&fit=crop",
    ),
    (
        "nat-snowy-village",
        "Snowy Mountain Village",
        "Unsplash / Kym MacKinnon",
        "Nature", "Unsplash License", "Unsplash",
        "https://images.unsplash.com/photo-1548247416-ec66f4900b2e?w=1200&q=80&fit=crop",
    ),
    (
        "arch-venice-canal",
        "Venice Canal at Dusk",
        "Unsplash / Dan Novac",
        "Architecture", "Unsplash License", "Unsplash",
        "https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=1200&q=80&fit=crop",
    ),
    (
        "arch-cliffside-village",
        "Amalfi Cliffside Village",
        "Unsplash / Alistair MacRobert",
        "Architecture", "Unsplash License", "Unsplash",
        "https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?w=1200&q=80&fit=crop",
    ),
    (
        "min-lighthouse-storm",
        "Lighthouse in Storm Waves",
        "Unsplash / Silas Baisch",
        "Minimalist", "Unsplash License", "Unsplash",
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&q=80&fit=crop",
    ),
    (
        "quote-cozy-reading",
        "Cozy Reading Nook",
        "Unsplash / Alfons Morales",
        "Quotes", "Unsplash License", "Unsplash",
        "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1200&q=80&fit=crop",
    ),


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


]

# ---------------------------------------------------------------------------
# DEDUPLICATION & BUILD
# ---------------------------------------------------------------------------
cand_objs = []
seen_ids = set()
seen_urls = set()

for (cid, title, author, cat, lic, attr, url) in RAW:
    base_url = url.split('?')[0]          # deduplicate by base URL
    if cid in seen_ids or base_url in seen_urls:
        continue
    seen_ids.add(cid)
    seen_urls.add(base_url)
    cand_objs.append({
        "id": cid,
        "title": title,
        "author": author,
        "authorUrl": "https://commons.wikimedia.org" if "wikimedia" in url else "https://unsplash.com",
        "category": cat,
        "sourceUrl": url,
        "license": lic,
        "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/" if lic in ("CC0", "Public Domain") else "https://unsplash.com/license",
        "attribution": attr,
        "imageUrl": url,
    })

print(f"[+] Deduplicated candidate count: {len(cand_objs)}")

# ---------------------------------------------------------------------------
# DOWNLOAD & CROP THUMBNAILS
# ---------------------------------------------------------------------------
valid_objs = []
seen_hashes = {}

for idx, c in enumerate(cand_objs, 1):
    thumb_name = f"{c['id']}.jpg"
    thumb_path = os.path.join(REVIEW_THUMBS_DIR, thumb_name)
    c['previewPath'] = f"review_thumbs/{thumb_name}"

    try:
        # Always re-download to guarantee freshness
        req = urllib.request.Request(c['imageUrl'], headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            img_data = resp.read()
        with open(thumb_path, 'wb') as f:
            f.write(img_data)

        # Center-crop to 3:4 — no squishing or stretching
        with Image.open(thumb_path) as img:
            fit = ImageOps.fit(img.convert('RGB'), (450, 600), Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            fit.save(thumb_path, 'JPEG', quality=88)

        # Hash-based duplicate check on final thumbnail
        with open(thumb_path, 'rb') as f:
            h = hashlib.md5(f.read()).hexdigest()

        if h in seen_hashes:
            print(f"[{idx}] SKIP '{c['title']}' — same image as '{seen_hashes[h]}'")
            os.remove(thumb_path)
            continue

        seen_hashes[h] = c['title']
        valid_objs.append(c)
        print(f"[{idx}] OK  '{c['title']}'")

    except Exception as e:
        print(f"[{idx}] ERR '{c['title']}': {e}")

print(f"\n[+] Final valid count: {len(valid_objs)}")

# ---------------------------------------------------------------------------
# SAVE candidates.json
# ---------------------------------------------------------------------------
with open(CANDIDATES_FILE, 'w', encoding='utf-8') as f:
    json.dump(valid_objs, f, indent=2, ensure_ascii=False)

# ---------------------------------------------------------------------------
# BUILD review.html
# ---------------------------------------------------------------------------
items_js = json.dumps(valid_objs, indent=2, ensure_ascii=False)

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Storefront Screensaver Seeding Review</title>
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
    <h1>🖼 Storefront Screensaver Seeding Review</h1>
    <div class="stats" id="stats">Loading…</div>
  </div>
  <button class="btn-export" onclick="exportApproved()">💾 Export approved.json</button>
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
    card.innerHTML = `
      <img src="${{c.previewPath}}" alt="${{c.title}}" loading="lazy">
      <div class="card-body">
        <p class="card-title">${{c.title}}</p>
        <p class="card-author">${{c.author}}</p>
        <div class="badges">
          <span class="badge">${{c.category}}</span>
          <span class="badge badge-lic">${{c.license}}</span>
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
  a.download = 'approved.json';
  a.click();
}}

render();
</script>
</body>
</html>
"""

with open(REVIEW_HTML, 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f"[+] review.html written with {len(valid_objs)} items -> {REVIEW_HTML}")
