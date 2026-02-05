#!/usr/bin/env python3
"""Test API connectivity"""

from urllib.request import urlopen
from urllib.error import URLError

try:
    # Test get merchant events
    r = urlopen('http://localhost:8000/api_get_merchant_events.py?merchantId=1')
    print('API accessible')
    print(r.read().decode()[:500])
except URLError as e:
    print('API not accessible:', e)
except Exception as e:
    print('Error:', e)
