Tornado Shortener
=================

URL Shortener based on Python, Tornado, Redis

Installation
------------

API
---

### /expand
Given a shortened URL or hash, returns the target (long) URL.

#### Authentication
None

#### Parameters
 - shortUrl - refers to one shortened link. e.g.: http://yourshortener.com/aN8gR.
 - hash - refers to one URL hash. e.g.: aN8gR.

**Note**
 - Either `shortUrl` or `hash` must be given as a parameter.
 - You can only provide one  `shortUrl` or `hash`.


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
        "long_url": "http://yourdomain.com/yourcategorie/2014-04-02/yourtitle",
        "short_url": "http://yourshortener.com/aN8gR",
      }
    ]
  },
  "status_code": 200,
  "status_txt": "OK"
}
```