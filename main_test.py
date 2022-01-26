#!/bin/python3
import hmac
import hashlib
import base64
import unittest
import requests
import time
import json

class TestIconomi(unittest.TestCase):

    # test api secret
    API_URL = "https://api.iconomi.com"
    API_SECRET = "<YOUR_SECRET>"
    API_KEY = "<YOUR_KEY>"

    def test_strategies(self):
        self.get('/v1/strategies')

    def test_activity(self):
        self.get('/v1/user/activity?type=FEES_AND_EARNINGS')

    def test_get_structure(self):
        ticker = '<YOUR_TICKER>'
        self.get('/v1/strategies/' + ticker + '/structure')

    def test_set_structure(self):
        ticker = "<YOUR_TICKER>"
        payload = {
          'ticker': ticker,
          'values': [
             {
               'rebalancedWeight': '0.5', 'assetTicker': 'ETH'
             },
             {
               'rebalancedWeight': '0.5', 'assetTicker': 'BTC'
             }
          ]
        }

        self.post('/v1/strategies/' + ticker + '/structure', payload)

    def test_withdraw(self):
        payload = {
            'amount': '0.02',
            'currency': 'ETH',
            'address': '<YOU_ETH_ADDRESS>'
        }

        self.post('/v1/user/withdraw', payload)

    def generate_signature(self, payload, request_type, request_path, timestamp): 
        query = request_path.find('?')
        if query != -1:
            request_path = request_path[0:query]
            
        data = ''.join([timestamp, request_type.upper(), request_path, payload]).encode()
        signed_data = hmac.new(self.API_SECRET.encode(), data, hashlib.sha512)
        return base64.b64encode(signed_data.digest())

    def get(self, api):      
        self.call('GET', api, '')

    def post(self, api, payload):
        self.call('POST', api, payload)
        
    def call(self, method, api, payload):
        timestamp = str(int(time.time() * 1000.0))

        jsonPayload = payload
        if method == 'POST':
          jsonPayload = json.dumps(payload)

        requestHeaders = { 
            'ICN-API-KEY' : self.API_KEY,
            'ICN-SIGN' : self.generate_signature(jsonPayload, method, api, timestamp),
            'ICN-TIMESTAMP' : timestamp
        }

        if method == 'GET': 
          response = requests.get(self.API_URL + api, headers = requestHeaders)
          if response.status_code == 200:
            print(json.dumps(json.loads(response._content), indent=4, sort_keys=True))
          else:
            print('Request did not succeed: ' + response.reason)
        elif method == 'POST':
          response = requests.post(self.API_URL + api, json = payload, headers = requestHeaders)
          if response.status_code == 200:
            print(json.dumps(json.loads(response._content), indent=4, sort_keys=True))
          else:
            print('Request did not succeed: ' + response.reason)

if __name__ == "__main__":
    unittest.main()
