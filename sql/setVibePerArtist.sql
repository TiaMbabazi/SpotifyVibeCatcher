-- 1. Add the column (only once)
ALTER TABLE play_history ADD COLUMN vibe_category TEXT;

-- 2. Shake Ahh Music
UPDATE play_history
SET vibe_category = 'Shake Ahh Music'
WHERE LOWER(genres) LIKE '%afrobeats%'
   OR LOWER(genres) LIKE '%amapiano%';

-- 3. Hot Girl Music
UPDATE play_history
SET vibe_category = 'Hot Girl Music'
WHERE LOWER(genres) LIKE '%rap%'
   OR LOWER(genres) LIKE '%hip hop%'
   OR LOWER(genres) LIKE '%trap%'
   OR LOWER(genres) LIKE '%drill%';

-- 4. Main Character Music
UPDATE play_history
SET vibe_category = 'Main Character Music'
WHERE LOWER(genres) LIKE '%rock%'
   OR LOWER(genres) LIKE '%indie%'
   OR LOWER(genres) LIKE '%alternative%'
   OR LOWER(genres) LIKE '%bedroom pop%'
   OR LOWER(genres) LIKE '%lo-fi%';

-- 5. White Girl Music
UPDATE play_history
SET vibe_category = 'White Girl Music'
WHERE LOWER(genres) LIKE '%pop%'
   OR LOWER(genres) LIKE '%electropop%'
   OR LOWER(genres) LIKE '%neo%'
   OR LOWER(genres) LIKE '%queer pop%';

-- 6. Everything else → Unknown
UPDATE play_history
SET vibe_category = 'Unknown'
WHERE vibe_category IS NULL;
