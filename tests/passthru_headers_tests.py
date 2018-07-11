import urllib2
import socket
import unittest
import mock

from urllib2 import _have_ssl, ssl, HTTPSHandler, build_opener
from arcrest.ags import MapService


class PassThruHeadersTestCase(unittest.TestCase):

    # Note: TEST_HEADER (or any mixed case in header name) is converted to
    # Test_header by urllib2; so testing that here
    _headers = {'Test_header': 'SomeValue'}

    @classmethod
    def mock_urlopen(cls, url, data=None,
                     timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                     cafile=None, capath=None, cadefault=False, context=None):

        # Check for passed-through headers
        if not isinstance(url, urllib2.Request) or \
                cls._headers.items()[0] not in url.header_items():
            raise urllib2.URLError('Headers not passed through')

        global _opener
        if cafile or capath or cadefault:
            if context is not None:
                raise ValueError(
                    "You can't pass both context and any of cafile, capath, "
                    "and cadefault"
                )
            if not _have_ssl:
                raise ValueError('SSL support not available')
            context = ssl.create_default_context(
                purpose=ssl.Purpose.SERVER_AUTH,
                cafile=cafile,
                capath=capath)
            https_handler = HTTPSHandler(context=context)
            opener = build_opener(https_handler)
        elif context:
            https_handler = HTTPSHandler(context=context)
            opener = build_opener(https_handler)
        elif _opener is None:
            _opener = opener = build_opener()
        else:
            opener = _opener
        return opener.open(url, data, timeout)

    def test_mapserver_passthru_headers(self):
        url = 'https://services.arcgisonline.com/arcgis/rest/services/' \
              'Demographics/USA_Population_Density/MapServer'

        with mock.patch('urllib2.urlopen', new=self.mock_urlopen) as mock_open:
            parsed_service = MapService(url, add_headers=self._headers)
            print(mock_open)
            assert 'title' in parsed_service.itemInfo


if __name__ == '__main__':
    unittest.main()
