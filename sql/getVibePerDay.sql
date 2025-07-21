create table vibePerHour as 
WITH hourly_vibe_counts AS (
    SELECT 
        DATE(hourly_time) as play_date,
        EXTRACT(HOUR FROM hourly_time) as hour_of_day,
        vibe_category,
        COUNT(*) as plays_count
    FROM play_history 
    WHERE vibe_category != 'Unknown'  -- Exclude unknown vibes for cleaner analysis
    GROUP BY DATE(hourly_time), EXTRACT(HOUR FROM hourly_time), vibe_category
),

-- Step 2: Calculate average plays per vibe per hour across all dates
average_hourly_vibes AS (
    SELECT 
        hour_of_day,
        vibe_category,
        AVG(plays_count) as avg_plays_per_hour
    FROM hourly_vibe_counts
    GROUP BY hour_of_day, vibe_category
),

-- Step 2b: Calculate top artist per hour across all days
hourly_artist_counts AS (
    SELECT 
        EXTRACT(HOUR FROM hourly_time) as hour_of_day,
        artist_name,
        COUNT(*) as total_plays
    FROM play_history 
    WHERE vibe_category != 'Unknown'
    GROUP BY EXTRACT(HOUR FROM hourly_time), artist_name
),

top_hourly_artists AS (
    SELECT 
        hour_of_day,
        artist_name as top_artist,
        total_plays as artist_plays,
        ROW_NUMBER() OVER (PARTITION BY hour_of_day ORDER BY total_plays DESC) as artist_rank
    FROM hourly_artist_counts
),

-- Step 2c: Calculate top song per hour across all days
hourly_song_counts AS (
    SELECT 
        EXTRACT(HOUR FROM hourly_time) as hour_of_day,
        track_name,
        artist_name,
        COUNT(*) as total_plays
    FROM play_history 
    WHERE vibe_category != 'Unknown'
    GROUP BY EXTRACT(HOUR FROM hourly_time), track_name, artist_name
),

top_hourly_songs AS (
    SELECT 
        hour_of_day,
        track_name as top_song,
        artist_name as song_artist,
        total_plays as song_plays,
        ROW_NUMBER() OVER (PARTITION BY hour_of_day ORDER BY total_plays DESC) as song_rank
    FROM hourly_song_counts
),

-- Step 3: Rank vibes by average plays for each hour
ranked_vibes AS (
    SELECT 
        hour_of_day,
        vibe_category,
        avg_plays_per_hour,
        ROW_NUMBER() OVER (PARTITION BY hour_of_day ORDER BY avg_plays_per_hour DESC) as vibe_rank
    FROM average_hourly_vibes
)

-- Step 4: Select the top vibe for each hour with top artist and song
SELECT 
    rv.hour_of_day,
    CASE 
        WHEN rv.hour_of_day = 0 THEN '12:00 AM'
        WHEN rv.hour_of_day < 12 THEN CONCAT(rv.hour_of_day, ':00 AM')
        WHEN rv.hour_of_day = 12 THEN '12:00 PM'
        ELSE CONCAT(rv.hour_of_day - 12, ':00 PM')
    END as time_display,
    rv.vibe_category as dominant_vibe,
    ROUND(rv.avg_plays_per_hour, 2) as avg_vibe_plays,
    tha.top_artist,
    tha.artist_plays,
    ths.top_song,
    ths.song_artist,
    ths.song_plays
FROM ranked_vibes rv
LEFT JOIN top_hourly_artists tha ON rv.hour_of_day = tha.hour_of_day AND tha.artist_rank = 1
LEFT JOIN top_hourly_songs ths ON rv.hour_of_day = ths.hour_of_day AND ths.song_rank = 1
WHERE rv.vibe_rank = 1
ORDER BY rv.hour_of_day;