import logging
import os

import redis
import tornado
import tornado.ioloop
import tornado.options

from .handler import IndexHandler, RedirectHandler, ExpandHandler, ShortHandler

# Define command line parameters.
tornado.options.define('port', type=int, default=int(os.environ.get('PORT', 8888)), help='Listen on this port')
tornado.options.define('domain', type=str, default=str(os.environ.get('DOMAIN', 'localhost:8888')),
                       help='The default domain for shortening URLs')
tornado.options.define('localhostonly', type=bool, default=bool(os.environ.get('LOCALHOSTONLY', False)),
                       help='Listen on localhost only')
tornado.options.define('salt', type=str, default=str(os.environ.get('SALT', '')),
                       help='A string influencing the generated hashes')
tornado.options.define('redis_host', type=str, default=str(os.environ.get('REDIS_HOST', 'localhost')),
                       help='The redis host')
tornado.options.define('redis_port', type=int, default=int(os.environ.get('REDIS_PORT', 6379)), help='The redis port')
tornado.options.define('redis_db', type=int, default=int(os.environ.get('REDIS_DB', 0)), help='The redis db')
tornado.options.define('redis_namespace', type=str, default=str(os.environ.get('REDIS_NAMESPACE', 'SHORT:')),
                       help='The redis namespace used for all keys')
tornado.options.define('redis_password', type=str, default=str(os.environ.get('REDIS_PASSWORD', '')),
                       help='The redis password')
tornado.options.define('ttl', type=int, default=int(os.environ.get('TTL', 0)),
                       help='The time to live in days of each link, 0 means forever')

# Get logger.
access_log = logging.getLogger('tornado.access')


# Define application.
class Application(tornado.web.Application):
    """
    Main Class for this application holding everything together.
    It defines the url scheme for the API endpoints, configures application
    settings, initializes a tornado Application instance and establishes
    db connections.
    """

    def __init__(self, default_domain='localhost', hash_salt='', redis_namespace='SHORT:',
                 redis_host='localhost', redis_port=6379, redis_db=0, redis_password=None, ttl=0):
        if not redis_password:
            redis_password = None
            using_redis_password = 'NO'
        else:
            using_redis_password = 'YES'

        logging.info(
            'Starting application with the following parameters: default_domain: {},'
            'hash_salt: {}, redis_namespace: {}, redis_host: {}, redis_port: {},'
            'redis_db: {}, redis_password: {}, ttl: {}'.format(
                default_domain, hash_salt, redis_namespace, redis_host, redis_port,
                redis_db, using_redis_password, ttl))

        # Define routes.
        handlers = [
            (r'/$', IndexHandler),
            (r'/expand/$', ExpandHandler),
            (r'/expand', ExpandHandler),
            (r'/shorten/$', ShortHandler),
            (r'/shorten$', ShortHandler),
            (r'/([a-zA-Z0-9]+)/$', RedirectHandler),
            (r'/([a-zA-Z0-9]+)$', RedirectHandler),
        ]

        # Configure application settings.
        settings = dict(
            gzip=True,
            default_domain=default_domain,
            hash_salt=hash_salt,
            redis_namespace=redis_namespace,
            ttl=ttl,
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
        )

        # Call super constructor to initiate a Tornado Application.
        tornado.web.Application.__init__(self, handlers, **settings)

        # Connect to Redis.
        self.redis = redis.StrictRedis(
            host=redis_host, port=redis_port, db=redis_db, password=redis_password, decode_responses=True)


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
                              tornado.options.options.redis_password,
                              int(tornado.options.options.ttl))
    if tornado.options.options.localhostonly:
        address = '127.0.0.1'
        logging.info('Listening to localhost only')
    else:
        address = ''
        logging.info('Listening to all addresses on all interfaces')
    application.listen(tornado.options.options.port, address=address, xheaders=True)
    tornado.ioloop.IOLoop.instance().start()


# Run main method if script is run from command line.
if __name__ == '__main__':
    main()
