```bash
pip install -r requirements.dev.txt
```

```sql
CREATE DATABASE sopapi;

CREATE TABLE public."GAME_MODES" (
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY,
    name text,
    description text,
    answer1 text,
    answer2 text,
    PRIMARY KEY (id)
);

CREATE TABLE public."PLAYLISTS" (
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY,
    title text NOT NULL,
    description text,
    field1 text,
    field2 text,
    PRIMARY KEY (id)
);

CREATE TABLE public."PLAYLIST_ITEMS" (
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY,
    playlist_id integer,
    url text,
    field1 text,
    field2 text,
    PRIMARY KEY (id)
);

CREATE TABLE public."USERS" (
    email text,
    username text,
    token text,
    refresh_token text,
    user_id text NOT NULL,
    session_id text,
    PRIMARY KEY (user_id)
);
```
