"""
Test suite for Catalog Studio endpoints and Pillow image operations.
"""

import os
import sys
import json
import unittest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PIL import Image
import catalog_studio as cs

class TestCatalogStudio(unittest.TestCase):
    def setUp(self):
        self.catalog = cs.load_catalog()
        self.orig_create_backup = cs.create_backup
        cs.create_backup = lambda: None

    def tearDown(self):
        cs.create_backup = self.orig_create_backup
        try:
            from generate_catalogs import generate_catalogs
            generate_catalogs()
        except Exception:
            pass

    def test_load_catalog(self):
        self.assertGreater(len(self.catalog), 0)
        item = self.catalog[0]
        self.assertIn('id', item)
        self.assertIn('title', item)
        self.assertIn('category', item)
        self.assertIn('tags', item)
        self.assertIsInstance(item['tags'], list)

    def test_tags_present_on_all_items(self):
        for item in self.catalog:
            self.assertIn('tags', item, f"Item {item.get('id')} missing tags")
            self.assertIsInstance(item['tags'], list, f"Item {item.get('id')} tags is not a list")
            self.assertGreater(len(item['tags']), 0, f"Item {item.get('id')} has empty tags list")

    def test_image_processing_pil(self):
        # Create test RGBA image
        img = Image.new('RGBA', (800, 600), color=(255, 0, 0, 128))
        from io import BytesIO
        buf = BytesIO()
        img.save(buf, format='PNG')
        raw_bytes = buf.getvalue()

        test_id = 'test-studio-sample-temp'
        res = cs.process_and_save_image(raw_bytes, test_id, is_png=True)
        self.assertEqual(res['format'], 'png')
        self.assertTrue(os.path.exists(os.path.join(cs.REPO_ROOT, res['fullRel'])))
        self.assertTrue(os.path.exists(os.path.join(cs.REPO_ROOT, res['thumbRel'])))

        # Clean up test files
        for p in [os.path.join(cs.REPO_ROOT, res['fullRel']), os.path.join(cs.REPO_ROOT, res['thumbRel'])]:
            if os.path.exists(p):
                os.remove(p)

    def test_credits_generation(self):
        cs.rebuild_credits_file(self.catalog)
        self.assertTrue(os.path.exists(cs.CREDITS_MD))

    def test_clean_filename_to_title(self):
        self.assertEqual(cs.clean_filename_to_title("foggy_mountain-pines_4k.png"), "Foggy Mountain Pines 4k")
        self.assertEqual(cs.clean_filename_to_title("minimalist-ocean.jpg"), "Minimalist Ocean")
        self.assertEqual(cs.clean_filename_to_title("artistic_flower.webp"), "Artistic Flower")

    def test_generate_unique_id(self):
        existing = {"misty-pines", "misty-pines-1"}
        new_id = cs.generate_unique_id("Misty Pines", existing)
        self.assertEqual(new_id, "misty-pines-2")

        brand_new_id = cs.generate_unique_id("Ocean Sunset", existing)
        self.assertEqual(brand_new_id, "ocean-sunset")

    def test_generate_default_tags(self):
        tags = cs.generate_default_tags("Majestic Mountain Sunset", ["Nature", "Landscape"])
        self.assertIn("nature", tags)
        self.assertIn("mountain", tags)
        self.assertIn("sunset", tags)
        self.assertIsInstance(tags, list)
        self.assertGreater(len(tags), 0)

    def test_bulk_add_screensavers(self):
        # Create temporary test image
        img = Image.new('RGB', (400, 600), color=(100, 150, 200))
        from io import BytesIO
        import base64
        buf = BytesIO()
        img.save(buf, format='JPEG')
        b64_data = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode('utf-8')

        initial_catalog = cs.load_catalog()
        initial_count = len(initial_catalog)

        test_items = [
            {
                "title": "Bulk Test Item Alpha",
                "category": ["Minimalist", "Art"],
                "author": "Test Author",
                "license": "CC0",
                "imageData": b64_data,
                "isPng": False
            },
            {
                "filename": "bulk_test_item_beta.jpg",
                "category": "Sci-Fi",
                "imageData": b64_data,
                "isPng": False
            }
        ]

        result = cs.bulk_add_screensavers(test_items)
        self.assertTrue(result['success'])
        self.assertEqual(result['addedCount'], 2)
        self.assertEqual(result['failedCount'], 0)

        updated_catalog = cs.load_catalog()
        self.assertEqual(len(updated_catalog), initial_count + 2)

        added_ids = [item['id'] for item in result['items']]
        self.assertIn('bulk-test-item-alpha', added_ids)
        self.assertIn('bulk-test-item-beta', added_ids)

        for added_item in result['items']:
            self.assertIn('tags', added_item)
            self.assertGreater(len(added_item['tags']), 0)
            self.assertIn('fullUrl', added_item)
            self.assertIn('thumbnailUrl', added_item)

            full_path = os.path.join(cs.REPO_ROOT, f"images/{added_item['id']}.jpg")
            thumb_path = os.path.join(cs.REPO_ROOT, f"images/thumbnails/{added_item['id']}.jpg")
            self.assertTrue(os.path.exists(full_path))
            self.assertTrue(os.path.exists(thumb_path))

            # Cleanup created image files
            if os.path.exists(full_path):
                os.remove(full_path)
            if os.path.exists(thumb_path):
                os.remove(thumb_path)

        # Restore catalog
        cs.save_catalog(initial_catalog)
        cs.rebuild_credits_file(initial_catalog)
        self.assertEqual(len(cs.load_catalog()), initial_count)

    def test_scan_folder_and_local_file_bulk_add(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create two test images in temp directory
            img1 = Image.new('RGB', (300, 400), color=(50, 100, 150))
            img1_path = os.path.join(temp_dir, "misty_forest_view.jpg")
            img1.save(img1_path, 'JPEG')

            img2 = Image.new('RGBA', (300, 400), color=(150, 50, 100, 200))
            img2_path = os.path.join(temp_dir, "minimalist_cat.png")
            img2.save(img2_path, 'PNG')

            # Verify directory scan logic
            valid_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}
            scanned = []
            for entry in os.scandir(temp_dir):
                ext = os.path.splitext(entry.name)[1].lower()
                if ext in valid_extensions:
                    scanned.append({
                        "filename": entry.name,
                        "title": cs.clean_filename_to_title(entry.name),
                        "path": entry.path,
                        "ext": ext.lstrip('.')
                    })
            self.assertEqual(len(scanned), 2)
            titles = {x['title'] for x in scanned}
            self.assertIn("Misty Forest View", titles)
            self.assertIn("Minimalist Cat", titles)

            # Test bulk_add_screensavers with localFilePath
            initial_catalog = cs.load_catalog()
            initial_count = len(initial_catalog)

            items_to_add = [
                {
                    "title": "Misty Forest View",
                    "localFilePath": img1_path,
                    "category": "Nature"
                },
                {
                    "title": "Minimalist Cat",
                    "localFilePath": img2_path,
                    "category": ["Minimalist", "Art"],
                    "isPng": True
                }
            ]

            result = cs.bulk_add_screensavers(items_to_add)
            self.assertTrue(result['success'])
            self.assertEqual(result['addedCount'], 2)

            for added in result['items']:
                full_path = os.path.join(cs.REPO_ROOT, f"images/{added['id']}.{added['fullUrl'].split('.')[-1]}")
                thumb_path = os.path.join(cs.REPO_ROOT, f"images/thumbnails/{added['id']}.{added['thumbnailUrl'].split('.')[-1]}")
                self.assertTrue(os.path.exists(full_path))
                self.assertTrue(os.path.exists(thumb_path))

                if os.path.exists(full_path):
                    os.remove(full_path)
                if os.path.exists(thumb_path):
                    os.remove(thumb_path)

            # Restore catalog
            cs.save_catalog(initial_catalog)
            cs.rebuild_credits_file(initial_catalog)
            self.assertEqual(len(cs.load_catalog()), initial_count)

if __name__ == '__main__':
    unittest.main()
