#!/usr/bin/env python
# coding=UTF-8
# Title:       handler.py
# Description: Contains request handler for this application
# Author       David Nellessen <david.nellessen@familo.net>
# Date:        4/2/14
# Note:        
#==============================================================================

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
    def store_url(self, url_hash, long_url):
        """
        Stores a long URL for the given url hash.
        """
        k = self.settings['redis_namespace'] + 'URLS:' + url_hash
        self.application.redis.set(k, long_url)
        if self.settings['ttl']:
            self.application.redis.expireat(k, int(time.time()) + self.settings['ttl'] * 24 * 60 * 60)

    def load_url(self, url_hash):
        """
        Loads the long URL for the given URL hash.
        """
        return self.application.redis.get(self.settings['redis_namespace'] + 'URLS:' + url_hash)



class RedirectHandler(BaseHandler):
    """
    Handles API requests for the / API endpoint.
    """

    def get(self, url_hash):
        """
        Redirects a short URL based on the given url hash.
        """
        long_url = self.load_url(str(url_hash))
        if not long_url:
            raise HTTPError(404)
        else:
            self.redirect(long_url, permanent=True)



class ExpandHandler(BaseHandler):
    """
    Handles API requests for the /expand API endpoint.
    """

    def get(self):
        """
        Given a shortened URL or hash, returns the target (long) URL.
        """
        short_url = self.get_argument('shortUrl', None) # Is decoded by Tornado.
        url_hash = self.get_argument('hash', None)

        # validate short url and hash.
        if not short_url and not url_hash:
            return self.finish({'status_code': 500, 'status_txt': 'MISSING_ARG_SHORTURL_OR_HASH', 'data': []})
        if short_url:
            try:
                url_hash_from_url = utils.get_hash_from_url(short_url)
            except:
                # TODO: Response differs from bitly
                return self.finish({'status_code': 500, 'status_txt': 'INVALID_ARG_SHORTURL', 'data': []})
            if url_hash and url_hash != url_hash_from_url:
                # TODO: Response differs from bitly
                return self.finish({'status_code': 500, 'status_txt': 'ARGS_DONT_MATCH', 'data': []})
            else: url_hash = url_hash_from_url

        long_url = self.load_url(url_hash)
        if not long_url:
            return self.finish({'status_code': 200, 'status_txt': 'OK', 'data': {'expand': [
                {'error': 'NOT_FOUND', 'hash': url_hash}
            ]}})
        else:
            return self.finish({'status_code': 200, 'status_txt': 'OK', 'data': {'expand': [
                {'long_url': long_url, 'hash': url_hash, 'short_url': short_url}
            ]}})


class ShortHandler(BaseHandler):
    """
    Handles API requests for the /shorten API endpoint.
    """

    def get(self):
        """
        Given a long URL, returns a short URL.
        """
        long_url = self.get_argument('longUrl', None) # Is decoded by Tornado.
        domain = self.get_argument('domain', self.settings['default_domain'])

        # Normalize and validate long_url.
        try:
            long_url = utils.normalize_url(long_url)
            assert utils.validate_url(long_url) == True
        except:
            logging.info('Wrong URL', exc_info=1)
            return self.finish({'status_code': 500, 'status_txt': 'INVALID_URI', 'data': []})

        # Validate domain.
        if not utils.validate_url('http://' + domain):
            return self.finish({'status_code': 500, 'status_txt': 'INVALID_ARG_DOMAIN', 'data': []})

        # Generate a unique hash, assemble short url and store result in Redis.
        url_hash = utils.generate_hash(self.application.redis,
                                       self.settings['redis_namespace'],
                                       self.settings['hash_salt'])
        short_url = 'http://' + domain + '/' + url_hash
        self.store_url(url_hash, long_url)

        # Return success response.
        data = {'long_url': long_url, 'url': short_url, 'hash': url_hash, 'global_hash': url_hash}
        self.finish({'status_code': 200, 'status_txt': 'OK', 'data': data})
