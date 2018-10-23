from . import *


class TestRemote(TestCase):


    def test_basics(self):

        url = url_for('images', filename='https://httpbin.org/image/jpeg', mode='crop', height=100, width=100)

        parsed_url = urlsplit(url)
        query_args = dict(parse_qsl(parsed_url.query))

        self.assertEqual(parsed_url.path, '/imgsizer/_')
        self.assertEqual(query_args.get('u'), 'https://httpbin.org/image/jpeg')

        response = self.client.get(url)
        self.assert200(response)

    def test_failure(self):

        url = url_for('images', filename='https://httpbin.org/status/418', mode='crop', height=100, width=100)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 418)
        
