#!/usr/bin/env python
# coding=UTF-8
# Title:       Tornado URL Shortener
# Description: The main application file. Run this to start the URL shortener webserver.
# Author       David Nellessen <david.nellessen@familo.net>
# Date:        4/2/14
# Note:        
#==============================================================================

# Import modules
import logging
import tornado, tornado.options, tornado.ioloop
from handler import RedirectHandler, ExpandHandler, ShortHandler
import redis


# Define command line parameters.
tornado.options.define("port", type=int, default=8888, help="Listen on this port")
tornado.options.define("domain", type=str, default="localhost:8888", help="The default domain for shortening URLs")
tornado.options.define("localhostonly", type=bool, default=False, help="Listen on localhost only")
tornado.options.define("salt", type=str, default='', help="A string influencing the generated hashes")
tornado.options.define("redis_namespace", type=str, default='SHORT:', help="The redis namespace used for all keys")
tornado.options.define("redis_host", type=str, default='localhost', help="The redis host")
tornado.options.define("redis_port", type=int, default=6379, help="The redis port")
tornado.options.define("redis_db", type=int, default=0, help="The redis db")
tornado.options.define("ttl", type=int, default=0, help="The time to live in days of each link, 0 means forever")


# Get logger.
access_log = logging.getLogger("tornado.access")


# Define application.
class Application(tornado.web.Application):
    """
    Main Class for this application holding everything together.
    It defines the url scheme for the API endpoints, configures application
    settings, initializes a tornado Application instance and establishes
    db connections.
    """
    def __init__(self, default_domain, hash_salt, redis_namespace, redis_host, redis_port, redis_db, ttl):
        # Define routes.
        handlers = [
            (r"/expand/$", ExpandHandler),
            (r"/expand", ExpandHandler),
            (r"/shorten/$", ShortHandler),
            (r"/shorten$", ShortHandler),
            (r"/([a-zA-Z0-9]*)/$", RedirectHandler),
            (r"/([a-zA-Z0-9]*)$", RedirectHandler),
        ]

        # Configure application settings.
        settings = dict(
            gzip = True,
            default_domain = default_domain,
            hash_salt = hash_salt,
            redis_namespace = redis_namespace,
            ttl = ttl,
        )

        # Call super constructor to initiate a Tornado Application.
        tornado.web.Application.__init__(self, handlers, **settings)

        # Connect to Redis.
        self.redis = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)


def main():
    """
    Main function to start the webserver application and listen on the specified port.
    """
    tornado.options.parse_command_line()
    application = Application(tornado.options.options.domain,
                              tornado.options.options.salt,
                              tornado.options.options.redis_namespace,
                              tornado.options.options.redis_host,
                              int(tornado.options.options.redis_port),
                              tornado.options.options.redis_db,
                              int(tornado.options.options.ttl))
    if tornado.options.options.localhostonly:
        address='127.0.0.1'
        logging.info("Listening to localhost only")
    else:
        address = ''
        logging.info("Listening to all addresses on all interfaces")
    application.listen(tornado.options.options.port, address=address, xheaders=True)
    tornado.ioloop.IOLoop.instance().start()



# Run main method if script is run from command line.
if __name__ == "__main__":
    main()
