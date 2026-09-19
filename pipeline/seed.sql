
-- CityPulse Seed Data

INSERT INTO cities (name, slug, country, tier, latitude, longitude, min_lat, max_lat, min_lon, max_lon)
VALUES ('Berlin', 'berlin', 'Germany', 'full', 52.5200, 13.4050, 52.3383, 52.6755, 13.0884, 13.7611);

INSERT INTO categories (slug, display_name, interest_group, default_hours_policy, default_dwell_minutes)
VALUES
  ('cafe', 'Café', 'coffee', 'unknown', 45),
  ('restaurant', 'Restaurant', 'food', 'unknown', 50),
  ('museum', 'Museum', 'culture', 'unknown', 120),
  ('gallery', 'Gallery', 'culture', 'unknown', 50);