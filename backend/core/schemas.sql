CREATE TABLE IF NOT EXISTS users (
  id BIGSERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reviews (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT,
  domain VARCHAR(64) NOT NULL,     -- 'health' | 'product'
  product VARCHAR(255) NOT NULL,
  text TEXT NOT NULL,
  rating FLOAT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reviews_domain ON reviews(domain);
CREATE INDEX IF NOT EXISTS idx_reviews_product ON reviews(product);

CREATE TABLE IF NOT EXISTS labels (
  id BIGSERIAL PRIMARY KEY,
  review_id BIGINT NOT NULL,
  sentiment VARCHAR(8),            -- 'neg'|'neu'|'pos'
  effectiveness VARCHAR(8),        -- 'low'|'med'|'high'
  side_effects JSONB,              -- ["nausea","headache",...]
  aspects JSONB,                   -- [{"aspect":"battery","polarity":"neg"},...]
  model_version VARCHAR(64),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_labels_review_id ON labels(review_id);
