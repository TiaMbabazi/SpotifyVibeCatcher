create table vibeperday as
WITH daily_vibe_counts AS (
    SELECT 
        DATE(hourly_time) as play_date,
        EXTRACT(DOW FROM hourly_time) as day_of_week, -- 0=Sunday, 1=Monday, etc.
        vibe_category,
        COUNT(*) as plays_count
    FROM play_history 
    WHERE vibe_category != 'Unknown'  -- Exclude unknown vibes
    GROUP BY DATE(hourly_time), EXTRACT(DOW FROM hourly_time), vibe_category
),

-- Step 2: Calculate average plays per vibe per day of week across all weeks
average_daily_vibes AS (
    SELECT 
        day_of_week,
        vibe_category,
        AVG(plays_count) as avg_plays_per_day
    FROM daily_vibe_counts
    GROUP BY day_of_week, vibe_category
),

-- Step 3: Rank vibes by average plays for each day of week
ranked_daily_vibes AS (
    SELECT 
        day_of_week,
        vibe_category,
        avg_plays_per_day,
        ROW_NUMBER() OVER (PARTITION BY day_of_week ORDER BY avg_plays_per_day DESC) as vibe_rank
    FROM average_daily_vibes
),

-- Step 4: Calculate top artist per day of week
daily_artist_counts AS (
    SELECT 
        EXTRACT(DOW FROM hourly_time) as day_of_week,
        artist_name,
        COUNT(*) as total_plays
    FROM play_history 
    WHERE vibe_category != 'Unknown'
    GROUP BY EXTRACT(DOW FROM hourly_time), artist_name
),

top_daily_artists AS (
    SELECT 
        day_of_week,
        artist_name as top_artist,
        total_plays as artist_plays,
        ROW_NUMBER() OVER (PARTITION BY day_of_week ORDER BY total_plays DESC) as artist_rank
    FROM daily_artist_counts
),

-- Step 5: Calculate top song per day of week
daily_song_counts AS (
    SELECT 
        EXTRACT(DOW FROM hourly_time) as day_of_week,
        track_name,
        artist_name,
        COUNT(*) as total_plays
    FROM play_history 
    WHERE vibe_category != 'Unknown'
    GROUP BY EXTRACT(DOW FROM hourly_time), track_name, artist_name
),

top_daily_songs AS (
    SELECT 
        day_of_week,
        track_name as top_song,
        artist_name as song_artist,
        total_plays as song_plays,
        ROW_NUMBER() OVER (PARTITION BY day_of_week ORDER BY total_plays DESC) as song_rank
    FROM daily_song_counts
)

-- Final result: Weekly profile with top vibe, artist, and song for each day
SELECT 
    rdv.day_of_week,
    CASE rdv.day_of_week
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END as day_name,
    rdv.vibe_category as dominant_vibe,
    ROUND(rdv.avg_plays_per_day, 2) as avg_vibe_plays,
    tda.top_artist,
    tda.artist_plays,
    tds.top_song,
    tds.song_artist,
    tds.song_plays
FROM ranked_daily_vibes rdv
LEFT JOIN top_daily_artists tda ON rdv.day_of_week = tda.day_of_week AND tda.artist_rank = 1
LEFT JOIN top_daily_songs tds ON rdv.day_of_week = tds.day_of_week AND tds.song_rank = 1
WHERE rdv.vibe_rank = 1
ORDER BY rdv.day_of_week;