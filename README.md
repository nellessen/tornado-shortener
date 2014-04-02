Tornado Shortener
=================

URL Shortener based on Python, Tornado, Redis



Installation
------------
```
pip install tornado redis
```



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
 - domain - (optional) the short domain to use; this can be a custom short domain. The default for this parameter
   can be configured. Passing a specific domain via this parameter will override the default settings.

##### Notes
Long URLs should be URL-encoded. You can not include a longUrl in the request that has &, ?, #, or other reserved
parameters without first encoding it.


#### Return Values
- url - the shortened URL.
- hash - an identifier for long_url which is unique.
- global_hash - the same as hash (might change when authentication is implemented)
- long_url - an echo back of the longUrl request parameter. This may not always be equal to the URL requested, as some
  URL normalization may occur (e.g., due to encoding differences, or case differences in the domain). This long_url
  will always be functionally identical the the request parameter.

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
    "url": "http://yourshortener.com/aN8gR"
  },
  "status_code": 200,
  "status_txt": "OK"
}
```