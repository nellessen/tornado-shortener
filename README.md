Tornado Shortener
=================

URL Shortener based on Python, Tornado, Redis



Installation
------------
```
apt-get install redis-server
pip install tornadoshortener  # preferably in a virtualenv
```


Quick Start
-----------
To run a webserver on a given port with a default domain *localhost* used for
short URLs run the following command:
```
tornadoshortener --port=80 --domain=localhost
```
This assumes you have redis listen on the standard port on localhost.
You can change your redis database connection settings with the parameters
`redis_host`, `redis_port` and `redis_db`. And you can also define a namespace
for redis under which all keys will be stored using the parameter `redis_namespace`.

### Hashes and Hash Salt
For every URL shortened by this application a uniquie hash is generated. This hash
is  based on the the current day and an incrementing index for the current day.
These two values are used to generate the final hash using [hashids](http://www.hashids.org/).
Note that collisions are prevented even if you run this application in multiple processes
all connected to the same Redis database, because the the index used for hash generation is
stored and incremented in Redis.

If you want the hashes to be more obscure you can provide a salt as the parameter `salt`.

### Time To Live
By default all URLs and hashes will live forever. If you want you can set a TTL
(time to live) for all URLs as the parameter `ttl`. Note that this will only
effect new URLs/hashes.

### Command-line Arguments and Environment Variables
Instead of using command-line arguments you can also use environment variables.
This makes especially sense if you want to hide your redis credentials from
the process list. The following table show the command-line parameters available
and the corresponding environment variables: [README.parameter.md](README.parameter.md).


### Advanced Setup
In a real-world scenario you would want to run multiple application process behind a load
balancer like [nginx](http://nginx.org/). You can find an nginx configuration in *conf/nginx.conf*
as well as a supervisor configuration in *conf/supervisord.conf*.


### Alternative URLs for iOS and Android Devices
The shortener support alternative URLs for iOS and Android devices. This way you can redirect
your mobile customers to specific pages. You can even start the app if you have registered an
URL Scheme. If you want to use that you can event provide a fallback URL which should than point
to the AppStore and PlayStore respectively.


API
---
Currently there is no support for authentication. Though there is a configurable
limit on API calls. All API endpoints return JSON.


### /expand
Given a shortened URL or hash, returns the target (long) URL.

#### Parameters
 - shortUrl - refers to one shortened link. e.g.: http://yourshortener.com/aN8gR.
 - hash - refers to one URL hash. e.g.: aN8gR.

##### Notes
Either `shortUrl` or `hash` must be given as a parameter.
You can only provide one  `shortUrl` or `hash`.


#### Return Values
- short_url - an echo back of the shortUrl request parameter.
- hash - an echo back of the hash request parameter.
- error - indicates there was an error retrieving data for a given shortUrl or hash. An example error is "NOT_FOUND".
- long_url - the URL that the requested short_url or hash points to.
- android_url - the Android URL that the requested short_url or hash points to.
- android_fallback_url - the Android fallback URL that the requested short_url or hash points to.
- ios_url - the iOS URL that the requested short_url or hash points to.
- ios_fallback_url - the iOS fallback URL that the requested short_url or hash points to.

#### Example Request
```
API Address: https://yourshortener.com/
GET /expand?shortUrl=http%3A%2F%2Fyourshortener.com%2FaN8gR
```

#### Example Response
```
{
  "data": {
    "expand": [
      {
        "long_url": "http://yourdomain.com/yourcategorie/2014-04-02/yourtitle/",
        "android_url": "familonet://",
        "android_fallback_url": "https://play.google.com/store/apps/details?id=net.familo.android",
        "ios_url": "familonet://",
        "ios_fallback_url": "https://itunes.apple.com/de/app/familonet-die-familien-app/id638696816",
        "short_url": "http://yourshortener.com/aN8gR",
        "hash": "aN8gR",
      }
    ]
  },
  "status_code": 200,
  "status_txt": "OK"
}
```


### /shorten
Given a long URL, returns a short URL.

#### Parameters
 - longUrl - a long URL to be shortened (example: http://yourdomain.com/yourcategorie/2014-04-02/yourtitle/).
 - androidUrl - an alternative for redirect for longUrl for Android devices (example: App start).
 - androidFallbackUrl - a fallback for android_url (example: Redirect to Play Store).
 - iosUrl - an alternative for redirect for longUrl for iOS devices (example: App start).
 - iosFallbackUrl - a fallback for android_url (example: Redirect to AppStore).
 - domain - (optional) the short domain to use; this can be a custom short domain. The default for this parameter
   can be configured. Passing a specific domain via this parameter will override the default settings.

##### Notes
Long URLs should be URL-encoded. You can not include a longUrl in the request that has &, ?, #, or other reserved
parameters without first encoding it.


#### Return Values
- url - the shortened URL.
- hash - an identifier which is unique.
- global_hash - the same as hash (might change when authentication is implemented)
- long_url - an echo back of the longUrl request parameter.
- android_url - an echo back of the androidUrl request parameter.
- android_fallback_url - an echo back of the androidFallbackUrl request parameter.
- ios_url - an echo back of the iosUrl request parameter.
- ios_fallback_url - an echo back of the iosFallbackUrl request parameter.

Note that the echo back URLs  may not always be equal to the URL requested, as some
URL normalization may occur (e.g., due to encoding differences, or case differences in the domain).
It will always be functionally identical the the request parameter.

#### Example Request
```
API Address: https://yourshortener.com/
GET /shorten?longUrl=http%3A%2F%2Fyourdomain.com%2Fyourcategorie%2F2014-04-02%2Fyourtitle%2F
```

#### Example Response
```
{
  "data": {
    "global_hash": "aN8gR",
    "hash": "aN8gR",
    "long_url": "http://yourdomain.com/yourcategorie/2014-04-02/yourtitle/",
    "android_url": null,
    "android_fallback_url": null,
    "ios_url": null,
    "ios_fallback_url": null,
    "url": "http://yourshortener.com/aN8gR"
  },
  "status_code": 200,
  "status_txt": "OK"
}
```
