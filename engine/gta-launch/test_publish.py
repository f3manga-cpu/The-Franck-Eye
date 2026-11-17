#!/usr/bin/env python3
"""Offline regression tests for scheduled GTA publishing; no network or writes to live docs."""
import importlib.util
import json
from datetime import datetime
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree

SOURCE = Path(__file__).with_name("publish.py")
spec = importlib.util.spec_from_file_location("gta_publish", SOURCE)
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)

class EditorialReleaseTests(unittest.TestCase):
    def test_schedule_boundary_and_no_future_leak(self):
        before = datetime.fromisoformat("2026-11-16T11:59:59+01:00")
        after = datetime.fromisoformat("2026-11-16T12:00:00+01:00")
        self.assertNotIn("signal-004", [s["slug"] for s in publisher.due_stories(before)])
        self.assertIn("signal-004", [s["slug"] for s in publisher.due_stories(after)])
        with tempfile.TemporaryDirectory() as tmp, patch.object(publisher, "OUT", Path(tmp)):
            publisher.write(publisher.due_stories(before))
            self.assertFalse((Path(tmp) / "signal-004.html").exists())
            self.assertNotIn("signal-004", (Path(tmp) / "feed.xml").read_text())
            publisher.write(publisher.due_stories(after))
            self.assertTrue((Path(tmp) / "signal-004.html").exists())
            root = ElementTree.parse(Path(tmp) / "feed.xml").getroot()
            links = [x.text for x in root.findall(".//item/link")]
            self.assertEqual(sum("signal-004" in (link or "") for link in links), 1)
            state = json.loads((Path(tmp) / "published.json").read_text())
            self.assertIs(state["coin_launched"], False)

    def test_share_links_are_opt_in_and_encoded(self):
        html = publisher.share_links("https://example.org/story?a=1&b=2", "A & B")
        self.assertIn("bsky.app/intent/compose?", html)
        self.assertIn("reddit.com/submit?", html)
        self.assertIn("A+%26+B", html)
        self.assertIn("target=\"_blank\"", html)
        self.assertNotIn("<script", html)

    def test_social_preview_metadata_is_canonical_and_escaped(self):
        story = publisher.due_stories(datetime.fromisoformat("2026-11-17T13:00:00+01:00"))[-1]
        html = publisher.article_page(story)
        self.assertIn('property="og:url" content="https://f3manga-cpu.github.io/The-Franck-Eye/gta/signal-005.html"', html)
        self.assertIn('name="twitter:card" content="summary_large_image"', html)
        self.assertIn('rel="canonical"', html)
        self.assertIn('Independent fiction; no live token.', html)

    def test_reject_duplicate_slugs(self):
        with tempfile.TemporaryDirectory() as tmp:
            queue = Path(tmp) / "queue.json"
            story = publisher.due_stories(datetime.fromisoformat("2026-11-16T12:00:00+01:00"))[0]
            queue.write_text(json.dumps({"stories": [story, story]}))
            with patch.object(publisher, "QUEUE", queue):
                with self.assertRaises(AssertionError):
                    publisher.due_stories(datetime.fromisoformat("2026-11-16T12:00:00+01:00"))

if __name__ == "__main__":
    unittest.main()
