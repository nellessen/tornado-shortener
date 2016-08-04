#!/usr/bin/env python
# coding=UTF-8
# Title:       test.py
# Description:
# Author       David Nellessen <david.nellessen@familo.net>
# Date:        4/2/14
# Note:
# =============================================================================

from __future__ import absolute_import, print_function, unicode_literals

# Import modules

# This test uses coroutine style.
import json
from tornado.testing import AsyncHTTPTestCase
from tornadoshortener.app import Application


class MyHTTPTest(AsyncHTTPTestCase):
    def get_app(self):
        return Application()

    def shorten(self):
        # Shorten an URL.
        self.http_client.fetch(
            self.get_url('/shorten?longUrl=http%3A%2F%2Fwww.familo.net'
                         '%2Fen%2F%3Fref%3Dhttp%253A%252F%252Ffamilo.net%252F'), self.stop)
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
        self.assertEqual(
            data.get('long_url'), 'http://www.familo.net/en/?ref=http%3A%2F%2Ffamilo.net%2F')
        self.assertEqual(data.get('url'), 'http://localhost/' + url_hash)

        return url_hash

    def shorten_mobile(self):
        # Shorten an URL.
        self.http_client.fetch(self.get_url(
            '/shorten?longUrl=http%3A%2F%2Fwww.familo.net%2Fen%2F%3Fref%3Dhttp%253A%252F%252Ffamil'
            'o.net%252F&androidUrl=familonet%3A%2F%2F&androidFallbackUrl=https%3A%2F%2Fplay.google'
            '.com%2Fstore%2Fapps%2Fdetails%3Fid%3Dnet.familo.android&iosUrl=familonet%3A%2F%2F&ios'
            'FallbackUrl=https%3A%2F%2Fitunes.apple.com%2Fde%2Fapp%2Ffamilonet-die-familien-app%2F'
            'id638696816'), self.stop)
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
        self.assertEqual(
            data.get('long_url'), 'http://www.familo.net/en/?ref=http%3A%2F%2Ffamilo.net%2F')
        self.assertEqual(data.get('android_url'), 'familonet://')
        self.assertEqual(
            data.get('android_fallback_url'),
            'https://play.google.com/store/apps/details?id=net.familo.android')
        self.assertEqual(data.get('ios_url'), 'familonet://')
        self.assertEqual(
            data.get('ios_fallback_url'),
            'https://itunes.apple.com/de/app/familonet-die-familien-app/id638696816')
        self.assertEqual(data.get('url'), 'http://localhost/' + url_hash)

        return url_hash

    def test_shortening(self):
        self.shorten()

    def test_shortening_mobile(self):
        self.shorten_mobile()

    def test_redirection(self):
        url_hash = self.shorten()
        self.http_client.fetch(self.get_url('/' + url_hash), self.stop)
        response = self.wait()
        self.assertIn(
            'www.familo.net/en/?ref=http%3A%2F%2Ffamilo.net%2F', response.effective_url)

    def test_redirection_mobile(self):
        url_hash = self.shorten_mobile()

        # Request as android devices.
        self.http_client.fetch(self.get_url('/' + url_hash), self.stop, user_agent='Android')
        response = self.wait()
        self.assertIn("text/html", response.headers.get('Content-Type', ""))
        self.assertIn("familonet://", response.body)
        self.assertIn(
            "https://play.google.com/store/apps/details?id=net.familo.android",
            response.body)

        # Request as iPhone devices.
        self.http_client.fetch(self.get_url('/' + url_hash), self.stop, user_agent='iPhone')
        response = self.wait()
        self.assertIn("text/html", response.headers.get('Content-Type', ""))
        self.assertIn("familonet://", response.body)
        self.assertIn(
            "https://itunes.apple.com/de/app/familonet-die-familien-app/id638696816",
            response.body)

        # Request as iPad devices.
        self.http_client.fetch(self.get_url('/' + url_hash), self.stop, user_agent='iPad')
        response = self.wait()
        self.assertIn("text/html", response.headers.get('Content-Type', ""))
        self.assertIn("familonet://", response.body)
        self.assertIn(
            "https://itunes.apple.com/de/app/familonet-die-familien-app/id638696816",
            response.body)

        # Request as other devices.
        self.http_client.fetch(self.get_url('/' + url_hash), self.stop)
        response = self.wait()
        self.assertIn('www.familo.net/en/', response.effective_url)

    def test_expand_hash(self):
        url_hash = self.shorten()

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
        self.assertEqual(
            data.get('long_url'), 'http://www.familo.net/en/?ref=http%3A%2F%2Ffamilo.net%2F')
        # self.assertEqual(data.get('short_url'), 'http://localhost/' + url_hash)

    def test_expand_hash_mobile(self):
        url_hash = self.shorten_mobile()

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
        self.assertEqual(
            data.get('long_url'), 'http://www.familo.net/en/?ref=http%3A%2F%2Ffamilo.net%2F')
        self.assertEqual(data.get('android_url'), 'familonet://')
        self.assertEqual(
            data.get('android_fallback_url'),
            'https://play.google.com/store/apps/details?id=net.familo.android')
        self.assertEqual(data.get('ios_url'), 'familonet://')
        self.assertEqual(
            data.get('ios_fallback_url'),
            'https://itunes.apple.com/de/app/familonet-die-familien-app/id638696816')
        # self.assertEqual(data.get('short_url'), 'http://localhost/' + url_hash)

    def test_expand_short_url(self):
        url_hash = self.shorten()

        # Expand URL.
        self.http_client.fetch(
            self.get_url('/expand?shortUrl=http%3A%2F%2Flocalhost%2F' + url_hash), self.stop)
        response = self.wait()
        self.assertIn("json", response.headers.get('Content-Type', ""))
        response.json = json.loads(response.body)

        # Test response.
        self.assertEqual(response.json.get('status_code'), 200)
        self.assertEqual(response.json.get('status_txt'), 'OK')
        expand = response.json.get('data', {}).get('expand', [])
        self.assertEqual(len(expand), 1)
        data = expand[0]
        # url_hash = data.get('hash')
        self.assertEqual(url_hash, url_hash)
        self.assertEqual(
            data.get('long_url'), 'http://www.familo.net/en/?ref=http%3A%2F%2Ffamilo.net%2F')
        self.assertEqual(
            data.get('short_url'), 'http://localhost/' + url_hash)

    def test_expand_short_url_mobile(self):
        url_hash = self.shorten_mobile()

        # Expand URL.
        self.http_client.fetch(
            self.get_url('/expand?shortUrl=http%3A%2F%2Flocalhost%2F' + url_hash), self.stop)
        response = self.wait()
        self.assertIn("json", response.headers.get('Content-Type', ""))
        response.json = json.loads(response.body)

        # Test response.
        self.assertEqual(response.json.get('status_code'), 200)
        self.assertEqual(response.json.get('status_txt'), 'OK')
        expand = response.json.get('data', {}).get('expand', [])
        self.assertEqual(len(expand), 1)
        data = expand[0]
        # url_hash = data.get('hash')
        self.assertEqual(url_hash, url_hash)
        self.assertEqual(
            data.get('long_url'), 'http://www.familo.net/en/?ref=http%3A%2F%2Ffamilo.net%2F')
        self.assertEqual(data.get('android_url'), 'familonet://')
        self.assertEqual(
            data.get('android_fallback_url'),
            'https://play.google.com/store/apps/details?id=net.familo.android')
        self.assertEqual(data.get('ios_url'), 'familonet://')
        self.assertEqual(
            data.get('ios_fallback_url'),
            'https://itunes.apple.com/de/app/familonet-die-familien-app/id638696816')
        self.assertEqual(data.get('short_url'), 'http://localhost/' + url_hash)
