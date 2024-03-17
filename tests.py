import unittest
import requests
import scrape as sc

# DECLARING TEST CLASSES
class TestScrapBeachesWebsite(unittest.TestCase):
    def test_successful_request(self):
        # Test HTTP request to a valid URL
        base_url = "https://www.worldbeachguide.com/usa/1"
        response = sc.access_beaches_website(base_url)
        self.assertEqual(response.status_code, 200)

    def test_invalid_url(self):
        # Test HTTP request to an invalid URL
        base_url = "https://www.worldbeachguide.com/nonexistent/"
        response = sc.access_beaches_website(base_url)
        self.assertEqual(response.status_code, 404)


class TestExtractHTMLFromScrapedPage(unittest.TestCase):
    def test_successful_response(self):
        # Test case for successful response (status code 200)
        response = MockResponse(
            status_code=200,
            text="<html><body><ul class='beach-list'><li>Beach 1</li><li>Beach 2</li></ul></body></html>")
        status_code, result = sc.extract_html_from_scraped_page(response)
        self.assertEqual(status_code, 200)
        self.assertEqual(str(result), '<ul class="beach-list"><li>Beach 1</li><li>Beach 2</li></ul>')
    
    def test_invalid_url(self):
        # Test case for invalid URL (status code 404)
        response = MockResponse(status_code=404)
        status_code, message = sc.extract_html_from_scraped_page(response)
        self.assertEqual(status_code, 404)
        self.assertEqual(message, "Invalid URL. Error 404")

    def test_timeout(self):
        # Test case for timeout (status code 408)
        response = MockResponse(status_code=408)
        status_code, message = sc.extract_html_from_scraped_page(response)
        self.assertEqual(status_code, 408)
        self.assertEqual(message, "Time Out. Error 408")

    def test_connection_error(self):
        # Test case for connection error (other status codes)
        response = MockResponse(status_code=503)
        status_code, message = sc.extract_html_from_scraped_page(response)
        self.assertEqual(status_code, 503)
        self.assertEqual(message, "Cannot connect to server. Error 503")

    def test_no_ul_element(self):
        # Test case for response with no <ul> element
        response = MockResponse(status_code=200, text="<html><body><div>No beach list</div></body></html>")
        status_code, result = sc.extract_html_from_scraped_page(response)
        self.assertEqual(status_code, 200)
        self.assertIsNone(result)  # Assert that result is None when <ul> element is not found

class TestFindAltLong(unittest.TestCase):

    def test_good_beach_name(self):
        beach_name = '''Lanikai Beach'''
        alt, long = sc.find_alt_long(beach_name)
        self.assertEqual(str(alt), '21.391734200000002')
        self.assertEqual(str(long), '-157.71481210121263')

    def test_invalid_beach_name(self):
        beach_name = '''invalid beach'''
        alt, long = sc.find_alt_long(beach_name)
        self.assertEqual(str(alt), '')
        self.assertEqual(str(long), '')


# DECLARING OTHER CLASSES
class MockResponse:
    def __init__(self, status_code=200, text=""):
        self.status_code = status_code
        self.text = text