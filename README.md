Back-end of a polling website.

### Running

Requires a Docker Bridge Network (cf `docker-compose.yaml`).

Requires the following env variables :

```bash
POSTGRES_USER="postgres user"
POSTGRES_SECRET="postgres secret"
POSTGRES_HOST="postgres host"
POSTGRES_DB="postgres name"
TWITCH_ID="twitch app id"
TWITCH_SECRET="twitch app secret"
BASE_URL="backend base url"
FRONT_BASE_URL="frontend base url"
ORIGINS='["frontend", "requests", "origin", "urls"]'
ENVIRONMENT="dev"
```

Run `start.sh` bash file.

While running, head to `/docs` route for API Documentation.

### Testing

Requires a Postgres database set up as in `app/tests/README.md`

Requires an enviromnent with both `requirements.txt` and `requirements.dev.txt` installed.
