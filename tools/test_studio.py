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

if __name__ == '__main__':
    unittest.main()
