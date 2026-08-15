import json

# Additional unique candidates to reach 75+ items
more_items = [
    # --- MORE FINE ART ---
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

    # --- MORE LANDMARKS & ARCHITECTURE ---
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

    # --- MORE SCI-FI & SPACE ---
    {
        "id": "nasa-jwst-carina-nebula-cliffs",
        "title": "Carina Nebula Cosmic Cliffs (JWST)",
        "author": "NASA / Space Telescope Science Institute",
        "authorUrl": "https://www.nasa.gov",
        "category": "Sci-Fi",
        "sourceUrl": "https://www.nasa.gov/image-article/carina-nebula-cosmic-cliffs/",
        "license": "Public Domain",
        "licenseUrl": "https://www.nasa.gov/multimedia/guidelines/index.html",
        "attribution": "NASA / STScI Public Domain",
        "imageUrl": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "nasa-hubble-pillars-creation",
        "title": "Pillars of Creation (Hubble)",
        "author": "NASA / ESA / Hubble Heritage Team",
        "authorUrl": "https://www.nasa.gov",
        "category": "Sci-Fi",
        "sourceUrl": "https://www.nasa.gov/image-feature/goddard/2017/hubble-takes-a-close-up-view-of-the-pillars-of-creation",
        "license": "Public Domain",
        "licenseUrl": "https://www.nasa.gov/multimedia/guidelines/index.html",
        "attribution": "NASA Public Domain",
        "imageUrl": "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "nasa-apollo8-earthrise-orbit",
        "title": "Earthrise from Moon Orbit (Apollo 8)",
        "author": "NASA / Bill Anders",
        "authorUrl": "https://www.nasa.gov",
        "category": "Sci-Fi",
        "sourceUrl": "https://www.nasa.gov/multimedia/imagegallery/image_feature_1249.html",
        "license": "Public Domain",
        "licenseUrl": "https://www.nasa.gov/multimedia/guidelines/index.html",
        "attribution": "NASA Public Domain",
        "imageUrl": "https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "nasa-juno-jupiter-clouds",
        "title": "Jupiter Swirling Clouds (Juno)",
        "author": "NASA / JPL-Caltech / SwRI / MSSS",
        "authorUrl": "https://www.nasa.gov",
        "category": "Sci-Fi",
        "sourceUrl": "https://www.jpl.nasa.gov/images/juno-image-of-jupiters-great-red-spot",
        "license": "Public Domain",
        "licenseUrl": "https://www.nasa.gov/multimedia/guidelines/index.html",
        "attribution": "NASA / JPL Public Domain",
        "imageUrl": "https://images.unsplash.com/photo-1614732414444-096e5f1122d5?auto=format&fit=crop&w=1200&q=80"
    }
]

print(f"Added {len(more_items)} extra unique items.")
