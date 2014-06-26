# Command-line Arguments and Environment Variables

Command-line Argument | Environment Variable | Default | Description
--- | --- | --- | ---
port | PORT | 8888 | Defines the port the server is listening on.
domain | DOMAIN | localhost:8888 | Defines the domain under which this application is available. Shorted URLs will point to this domain by default.
localhostonly | LOCALHOSTONLY | False | If True the application listens on localhost only. This makes sense if you setup this application behind a load balancer like nginx.
salt | SALT | "" | An additional salt to obscure hashes generated for shot URLs.
redis_host | REDIS_HOST | "localhost" | The Redis host you want to connect to. All persistent data will be stored in Redis.
redis_port | REDIS_PORT | 6379 | The port Redis is listening on.
redis_db | REDIS_DB | 0 | The Redis DB you want to connect to. Redis supports multiple DBs identified by integers 0, 1, 2,...
redis_namespace | REDIS_NAMESPACE | "SHORT:" | All Redis keys will be prefixed with this string.
redis_password | REDIS_PASSWORD | "" | The Redis password, "" meaning no password.
ttl | TTL | 0 | The time to live in days of each link, 0 meaning forever.
logging | - | "info" | The loglevel for this application ("debug", "info", "warning", "error")