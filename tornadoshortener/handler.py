#!/usr/bin/env python
# coding=UTF-8
# Title:       handler.py
# Description: Contains request handler for this application
# Author       David Nellessen <david.nellessen@familo.net>
# Date:        4/2/14
# Note:
# =============================================================================

# Import modules
import logging
import time
from tornado.web import RequestHandler
from tornado.web import HTTPError
import utils


class BaseHandler(RequestHandler):
    """
    A base class with common methods for all request handlers.
    """
    def store_url(self, url_hash, long_url, android_url=None,
                  android_fallback_url=None, ios_url=None, ios_fallback_url=None):
        """
        Stores a long URL for the given url hash. You can specify additional URLS
        for ios and android devices.
        """
        ttl = int(time.time()) + self.settings['ttl'] * 24 * 60 * 60
        key_prefix = self.settings['redis_namespace'] + 'URLS:' + url_hash
        pipe = self.application.redis.pipeline()

        k = key_prefix + ''
        pipe.set(k, long_url)
        if self.settings['ttl']:
            pipe.expireat(k, ttl)

        if android_url:
            k = key_prefix + ':android_url'
            pipe.set(k, android_url)
            if self.settings['ttl']:
                pipe.expireat(k, ttl)

        if android_fallback_url:
            k = key_prefix + ':android_fallback_url'
            pipe.set(k, android_fallback_url)
            if self.settings['ttl']:
                pipe.expireat(k, ttl)

        if ios_url:
            k = key_prefix + ':ios_url'
            pipe.set(k, ios_url)
            if self.settings['ttl']:
                pipe.expireat(k, ttl)

        if ios_fallback_url:
            k = key_prefix + ':ios_fallback_url'
            pipe.set(k, ios_fallback_url)
            if self.settings['ttl']:
                pipe.expireat(k, ttl)

        pipe.execute()

    def load_url(self, url_hash):
        """
        Loads the long URL for the given URL hash.
        """
        return self.application.redis.get(self.settings['redis_namespace'] + 'URLS:' + url_hash)

    def load_urls(self, url_hash):
        """
        Loads the long URL for the given URL hash as well as the alternative URLs
        for ios and android devices.

        @returns: Returns the URLs as a tuple
                  (long_url, android_url, android_fallback_url, ios_url, ios_fallback_url)
        """
        key_prefix = self.settings['redis_namespace'] + 'URLS:' + url_hash
        pipe = self.application.redis.pipeline()

        k = key_prefix + ''
        pipe.get(k)
        k = key_prefix + ':android_url'
        pipe.get(k)
        k = key_prefix + ':android_fallback_url'
        pipe.get(k)
        k = key_prefix + ':ios_url'
        pipe.get(k)
        k = key_prefix + ':ios_fallback_url'
        pipe.get(k)

        result = pipe.execute()

        return (result[0], result[1], result[2], result[3], result[4])


class RedirectHandler(BaseHandler):
    """
    Handles API requests for the / API endpoint.
    """

    def get(self, url_hash):
        """
        Redirects a short URL based on the given url hash.
        """
        long_url, android_url, android_fallback_url, \
            ios_url, ios_fallback_url = self.load_urls(str(url_hash))

        if not long_url:
            raise HTTPError(404)
        else:
            user_agent = self.request.headers.get('User-Agent', '')
            if android_url and 'Android' in user_agent:
                logging.debug('Redirect Android device')
                self.redirect_android(android_url, android_fallback_url)
                return
            elif ios_url and ('iPhone' in user_agent or 'iPad' in user_agent):
                logging.debug('Redirect iOS device')
                self.redirect_ios(ios_url, ios_fallback_url)
                return
            else:
                logging.debug('Default redirect')
                self.redirect(long_url, permanent=True)

    def redirect_android(self, url, url_fallback=None):
        if url_fallback:
            self.render('redirect.android.fallback.html', url=url, url_fallback=url_fallback)
        else:
            self.render('redirect.android.html', url=url, url_fallback=url_fallback)

    def redirect_ios(self, url, url_fallback=None):
        if url_fallback:
            self.render('redirect.ios.fallback.html', url=url, url_fallback=url_fallback)
        else:
            self.render('redirect.ios.html', url=url, url_fallback=url_fallback)


class ExpandHandler(BaseHandler):
    """
    Handles API requests for the /expand API endpoint.
    """

    def get(self):
        """
        Given a shortened URL or hash, returns the target (long) URL.
        """
        short_url = self.get_argument('shortUrl', None)  # Is decoded by Tornado.
        url_hash = self.get_argument('hash', None)

        # validate short url and hash.
        if not short_url and not url_hash:
            return self.finish(
                {'status_code': 500, 'status_txt': 'MISSING_ARG_SHORTURL_OR_HASH', 'data': []})
        if short_url:
            try:
                url_hash_from_url = utils.get_hash_from_url(short_url)
            except:
                # TODO: Response differs from bitly
                return self.finish(
                    {'status_code': 500, 'status_txt': 'INVALID_ARG_SHORTURL', 'data': []})
            if url_hash and url_hash != url_hash_from_url:
                # TODO: Response differs from bitly
                return self.finish(
                    {'status_code': 500, 'status_txt': 'ARGS_DONT_MATCH', 'data': []})
            else:
                url_hash = url_hash_from_url

        long_url, android_url, android_fallback_url, \
            ios_url, ios_fallback_url = self.load_urls(url_hash)
        if not long_url:
            return self.finish({
                'status_code': 200,
                'status_txt': 'OK',
                'data': {
                    'expand': [{'error': 'NOT_FOUND', 'hash': url_hash}]
                }
            })
        else:
            return self.finish({
                'status_code': 200,
                'status_txt': 'OK',
                'data': {
                    'expand': [{
                        'long_url': long_url,
                        'android_url': android_url,
                        'android_fallback_url': android_fallback_url,
                        'ios_url': ios_url,
                        'ios_fallback_url': ios_fallback_url,
                        'hash': url_hash,
                        'short_url': short_url
                    }]
                }
            })


class ShortHandler(BaseHandler):
    """
    Handles API requests for the /shorten API endpoint.
    """

    def get(self):
        """
        Given a long URL, returns a short URL.
        """
        long_url = self.get_argument('longUrl', None)  # decoded by Tornado.
        android_url = self.get_argument('androidUrl', None)  # decoded by Tornado.
        android_fallback_url = self.get_argument('androidFallbackUrl', None)  # decoded by Tornado.
        ios_url = self.get_argument('iosUrl', None)  # decoded by Tornado.
        ios_fallback_url = self.get_argument('iosFallbackUrl', None)  # decoded by Tornado.
        domain = self.get_argument('domain', self.settings['default_domain'])

        # Normalize and validate long_url.
        try:
            long_url = utils.normalize_url(long_url)
            assert utils.validate_url(long_url) is True
            if android_url:
                # TODO: Validate and normalize!
                pass
                # android_url = utils.normalize_url(android_url)
                # assert utils.validate_url(android_url) is True
            if android_fallback_url:
                android_fallback_url = utils.normalize_url(android_fallback_url)
                assert utils.validate_url(android_fallback_url) is True
            if ios_url:
                # TODO: Validate and normalize!
                pass
                # ios_url = utils.normalize_url(ios_url)
                # assert utils.validate_url(ios_url) is True
            if ios_fallback_url:
                ios_fallback_url = utils.normalize_url(ios_fallback_url)
                assert utils.validate_url(ios_fallback_url) is True
        except:
            logging.info('Wrong URL', exc_info=1)
            return self.finish({'status_code': 500, 'status_txt': 'INVALID_URI', 'data': []})

        # Validate domain.
        if not utils.validate_url('http://' + domain):
            return self.finish(
                    {'status_code': 500, 'status_txt': 'INVALID_ARG_DOMAIN', 'data': []})

        # Generate a unique hash, assemble short url and store result in Redis.
        url_hash = utils.generate_hash(self.application.redis,
                                       self.settings['redis_namespace'],
                                       self.settings['hash_salt'])
        short_url = 'http://' + domain + '/' + url_hash
        self.store_url(url_hash, long_url, android_url,
                       android_fallback_url, ios_url, ios_fallback_url)

        # Return success response.
        data = {
            'long_url': long_url,
            'android_url': android_url,
            'android_fallback_url': android_fallback_url,
            'ios_url': ios_url,
            'ios_fallback_url': ios_fallback_url,
            'url': short_url,
            'hash': url_hash,
            'global_hash': url_hash
        }
        self.finish({'status_code': 200, 'status_txt': 'OK', 'data': data})
