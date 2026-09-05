-- ============================================
-- CityPulse Database Schema
-- ============================================

CREATE TABLE cities (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    country TEXT NOT NULL,
    tier TEXT NOT NULL CHECK (tier IN ('full', 'core')),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    min_lat DOUBLE PRECISION,
    max_lat DOUBLE PRECISION,
    min_lon DOUBLE PRECISION,
    max_lon DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE categories (
    id BIGSERIAL PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    interest_group TEXT NOT NULL
        CHECK (interest_group IN ('coffee','food','culture','nature','nightlife','shopping')),
    default_hours_policy TEXT NOT NULL
        CHECK (default_hours_policy IN ('always_open','unknown')),
    default_dwell_minutes INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE places (
    id BIGSERIAL PRIMARY KEY,
    city_id BIGINT NOT NULL REFERENCES cities(id),
    category_id BIGINT NOT NULL REFERENCES categories(id),
    osm_type TEXT NOT NULL CHECK (osm_type IN ('node','way','relation')),
    osm_id BIGINT NOT NULL,
    name TEXT,
    geom geography(Point, 4326) NOT NULL,
    opening_hours_raw TEXT,
    hours_policy TEXT NOT NULL
        CHECK (hours_policy IN ('parsed','always_open','unknown')),
    price_level INTEGER CHECK (price_level BETWEEN 1 AND 4),
    price_band_source TEXT
        CHECK (price_band_source IN ('osm_tag','imputed_model','manual')),
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (osm_type, osm_id)
);

CREATE TABLE opening_hours (
    id BIGSERIAL PRIMARY KEY,
    place_id BIGINT NOT NULL REFERENCES places(id) ON DELETE CASCADE,
    weekday INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6),
    opens_at TIME NOT NULL,
    closes_at TIME NOT NULL,
    crosses_midnight BOOLEAN NOT NULL DEFAULT FALSE,
    parse_confidence TEXT NOT NULL
        CHECK (parse_confidence IN ('exact','approximate'))
);

CREATE TABLE ingest_runs (
    id BIGSERIAL PRIMARY KEY,
    city_id BIGINT NOT NULL REFERENCES cities(id),
    category_id BIGINT REFERENCES categories(id),
    source TEXT NOT NULL CHECK (source IN ('overpass','geofabrik')),
    bbox TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    status TEXT NOT NULL CHECK (status IN ('running','success','failed')),
    places_found INTEGER NOT NULL DEFAULT 0,
    places_inserted INTEGER NOT NULL DEFAULT 0,
    places_updated INTEGER NOT NULL DEFAULT 0,
    error_message TEXT
);

-- ============================================
-- Indexes
-- ============================================

CREATE INDEX idx_places_geom ON places USING GIST (geom);
CREATE INDEX idx_places_city_id ON places(city_id);
CREATE INDEX idx_places_category_id ON places(category_id);
CREATE INDEX idx_opening_hours_place_weekday ON opening_hours(place_id, weekday);