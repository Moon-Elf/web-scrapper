import unittest
from crawl import *


class TestCrawl(unittest.TestCase):
    def test_normalize_url_protocol(self):
        # HTTP vs HTTPS
        input_url = "http://blog.boot.dev/path"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_trailing_slash(self):
        # Trailing slash removal
        input_url = "https://blog.boot.dev/path/"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_root_path(self):
        # Bare domain vs domain with slash
        input_url = "https://blog.boot.dev/"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev"
        self.assertEqual(actual, expected)

    def test_normalize_url_bare_domain(self):
        # Bare domain without trailing slash
        input_url = "https://blog.boot.dev"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev"
        self.assertEqual(actual, expected)

    def test_normalize_url_case_insensitivity(self):
        # Hostnames are case-insensitive
        input_url = "https://BLOG.boot.dev/path"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_nested_path(self):
        # Deeply nested path with trailing slash
        input_url = "https://blog.boot.dev/path/subpath/page/"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path/subpath/page"
        self.assertEqual(actual, expected)


class TestGetHeadingFromHTML(unittest.TestCase):
    def test_h1_present(self):
        input_body = "<html><body><h1>Main Title</h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Main Title"
        self.assertEqual(actual, expected)

    def test_h2_fallback(self):
        input_body = "<html><body><h2>Secondary Title</h2></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Secondary Title"
        self.assertEqual(actual, expected)

    def test_h1_takes_priority_over_h2(self):
        input_body = """<html><body>
            <h1>Primary</h1>
            <h2>Secondary</h2>
        </body></html>"""
        actual = get_heading_from_html(input_body)
        expected = "Primary"
        self.assertEqual(actual, expected)

    def test_no_heading_found(self):
        input_body = "<html><body><p>Just a paragraph.</p></body></html>"
        actual = get_heading_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_heading_with_nested_tags(self):
        input_body = "<html><body><h1>Welcome <span>Friend</span></h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Welcome Friend"
        self.assertEqual(actual, expected)


class TestGetFirstParagraphFromHTML(unittest.TestCase):
    def test_simple_paragraph(self):
        input_body = "<html><body><p>Only paragraph.</p></body></html>"
        actual = get_first_paragraph_from_html(input_body)
        expected = "Only paragraph."
        self.assertEqual(actual, expected)

    def test_no_main_uses_first_p(self):
        input_body = """<html><body>
            <p>First one.</p>
            <p>Second one.</p>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "First one."
        self.assertEqual(actual, expected)

    def test_main_present_ignores_outside_p(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Inside main.</p>
                <p>Second inside main.</p>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Inside main."
        self.assertEqual(actual, expected)

    def test_no_paragraph_found(self):
        input_body = "<html><body><h1>No paragraphs here</h1></body></html>"
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_empty_main_falls_back(self):
        input_body = """<html><body>
            <main></main>
            <p>Fallback paragraph.</p>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

class TestGetURLsFromHTML(unittest.TestCase):
    def test_absolute_url(self):
        base_url = "https://crawler-test.com"
        html = '<a href="https://example.com/page">Visit</a>'

        actual = get_urls_from_html(html, base_url)

        self.assertEqual(actual, ["https://example.com/page"])

    def test_relative_url(self):
        base_url = "https://crawler-test.com"
        html = '<a href="/about">About</a>'

        actual = get_urls_from_html(html, base_url)

        self.assertEqual(actual, ["https://crawler-test.com/about"])

    def test_multiple_links(self):
        base_url = "https://crawler-test.com"
        html = """
            <a href="/one">One</a>
            <a href="/two">Two</a>
            <a href="https://example.com/three">Three</a>
        """

        actual = get_urls_from_html(html, base_url)

        expected = [
            "https://crawler-test.com/one",
            "https://crawler-test.com/two",
            "https://example.com/three",
        ]
        self.assertEqual(actual, expected)

class TestGetImagesFromHTML(unittest.TestCase):
    def test_absolute_image_url(self):
        base_url = "https://crawler-test.com"
        html = '<img src="https://images.example.com/logo.png" alt="Logo">'

        actual = get_images_from_html(html, base_url)

        self.assertEqual(actual, ["https://images.example.com/logo.png"])

    def test_relative_image_url(self):
        base_url = "https://crawler-test.com"
        html = '<img src="/images/logo.png" alt="Logo">'

        actual = get_images_from_html(html, base_url)

        self.assertEqual(actual, ["https://crawler-test.com/images/logo.png"])

    def test_missing_src_is_ignored(self):
        base_url = "https://crawler-test.com"
        html = """
            <img alt="No source">
            <img src="/valid.png" alt="Valid">
        """

        actual = get_images_from_html(html, base_url)

        self.assertEqual(actual, ["https://crawler-test.com/valid.png"])

class TestExtractPageData(unittest.TestCase):
    def test_extract_page_data_basic(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://crawler-test.com/link1"],
            "image_urls": ["https://crawler-test.com/image1.jpg"],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_with_main_tag(self):
        input_url = "https://blog.boot.dev"
        input_body = """<html><body>
            <h2>Blog Post</h2>
            <p>Outside paragraph, should be ignored.</p>
            <main>
                <p>Main content paragraph.</p>
            </main>
            <a href="https://other.com/page">External</a>
            <img src="pic.png">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://blog.boot.dev",
            "heading": "Blog Post",
            "first_paragraph": "Main content paragraph.",
            "outgoing_links": ["https://other.com/page"],
            "image_urls": ["https://blog.boot.dev/pic.png"],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_missing_elements(self):
        input_url = "https://crawler-test.com"
        input_body = "<html><body><p>No heading here.</p></body></html>"
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "",
            "first_paragraph": "No heading here.",
            "outgoing_links": [],
            "image_urls": [],
        }
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()