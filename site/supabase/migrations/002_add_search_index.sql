CREATE INDEX idx_strains_name_search ON strains USING gin(to_tsvector('english', name));
