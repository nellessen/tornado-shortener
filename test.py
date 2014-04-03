#!/usr/bin/env python
# coding=UTF-8
# Title:       test.py
# Description: 
# Author       David Nellessen <david.nellessen@familo.net>
# Date:        4/2/14
# Note:        
#==============================================================================

# Import modules

# This test uses coroutine style.
import json
from tornado.testing import AsyncHTTPTestCase
from app import Application


class MyHTTPTest(AsyncHTTPTestCase):
    def get_app(self):
        return Application()

    def test_shortening(self):
        # Shorten an URL.
        self.http_client.fetch(self.get_url('/shorten?longUrl=http%3A%2F%2Fwww.familo.net%2Fen%2F'), self.stop)
        response = self.wait()
        self.assertIn("json", response.headers.get('Content-Type', ""))
        response.json = json.loads(response.body)

        # Test response.
        self.assertEqual(response.json.get('status_code'), 200)
        self.assertEqual(response.json.get('status_txt'), 'OK')
        data = response.json.get('data', {})
        url_hash = data.get('hash')
        global_hash = data.get('global_hash')
        self.assertIsNotNone(url_hash)
        self.assertEqual(url_hash, global_hash)
        self.assertEqual(data.get('long_url'), 'http://www.familo.net/en/')
        self.assertEqual(data.get('url'), 'http://localhost/' + url_hash)

        return url_hash


    def test_redirection(self):
        url_hash = self.test_shortening()
        self.http_client.fetch(self.get_url('/' + url_hash), self.stop)
        response = self.wait()
        self.assertIn('www.familo.net/en/', response.effective_url)


    def test_expand_hash(self):
        url_hash = self.test_shortening()

        # Expand URL.
        self.http_client.fetch(self.get_url('/expand?hash=' + url_hash), self.stop)
        response = self.wait()
        self.assertIn("json", response.headers.get('Content-Type', ""))
        response.json = json.loads(response.body)

        # Test response.
        self.assertEqual(response.json.get('status_code'), 200)
        self.assertEqual(response.json.get('status_txt'), 'OK')
        expand = response.json.get('data', {}).get('expand', [])
        self.assertEqual(len(expand), 1)
        data = expand[0]
        url_hash = data.get('hash')
        self.assertEqual(url_hash, url_hash)
        self.assertEqual(data.get('long_url'), 'http://www.familo.net/en/')
        #self.assertEqual(data.get('short_url'), 'http://localhost/' + url_hash)


    def test_expand_short_url(self):
        url_hash = self.test_shortening()

        # Expand URL.
        self.http_client.fetch(self.get_url('/expand?shortUrl=http%3A%2F%2Flocalhost%2F' + url_hash), self.stop)
        response = self.wait()
        self.assertIn("json", response.headers.get('Content-Type', ""))
        response.json = json.loads(response.body)

        # Test response.
        self.assertEqual(response.json.get('status_code'), 200)
        self.assertEqual(response.json.get('status_txt'), 'OK')
        expand = response.json.get('data', {}).get('expand', [])
        self.assertEqual(len(expand), 1)
        data = expand[0]
        #url_hash = data.get('hash')
        self.assertEqual(url_hash, url_hash)
        self.assertEqual(data.get('long_url'), 'http://www.familo.net/en/')
        self.assertEqual(data.get('short_url'), 'http://localhost/' + url_hash)
