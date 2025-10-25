CREATE TABLE IF NOT EXISTS users (
  id BIGSERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reviews (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
  domain VARCHAR(64) NOT NULL,
  product VARCHAR(255) NOT NULL,
  text TEXT NOT NULL,
  rating FLOAT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reviews_domain ON reviews(domain);
CREATE INDEX IF NOT EXISTS idx_reviews_product ON reviews(product);

CREATE TABLE IF NOT EXISTS labels (
  id BIGSERIAL PRIMARY KEY,
  review_id BIGINT NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
  sentiment VARCHAR(16),             -- e.g. 'negative'|'neutral'|'positive'
  effectiveness VARCHAR(16),         -- e.g. 'low'|'med'|'high' (for meds / perceived efficacy)
  side_effects JSONB,                -- ["nausea","headache",...]
  aspects JSONB,                     -- [{"aspect":"battery life","polarity":"negative"}, ...]
  model_version VARCHAR(64),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_labels_review_id ON labels(review_id);
