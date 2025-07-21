# 🎧 SpotifyVibeCatcher

**SpotifyVibeCatcher** is a personalized Spotify data analytics project that explores your listening patterns across **hours**, **days**, and **seasons**. It visualizes your top songs, artists, and categorized “vibes” using Python, PostgreSQL, and Streamlit.

---

## Overview

This project analyzes personal streaming history by:
- Assigning each song a **vibe category** (Hot Girl, Main Character, Shake Ahh, White Girl) based on artist genres
- Aggregating listening trends by hour, day, and season
- Visualizing patterns through an interactive dashboard

---

## Features

- Cleaned and transformed Spotify streaming data using **Python** and **PostgreSQL**
- Enriched with **Spotify API** for track and artist metadata
- Vibe categories assigned through custom SQL logic
- Interactive dashboard built with **Streamlit**, **Seaborn**, and **Matplotlib**
- Future expansion with **React** frontend and **Figma** designs for user interactivity

---

## Folder Structure
- app.py # Streamlit dashboard app
- generateIDs.py # Adds Spotify track and artist IDs
- spotifygenre.py # Gets artist genres from Spotify
- TranformTime.py # Creates hourly timestamps
- setVibePerArtist.sql # Assigns vibes based on genres
- getVibePerHour.sql # Query: top vibe/artist/song per hour
- getVibePerDay.sql # Query: top vibe/artist/song per day
- getVibePerSeason.sql # Query: top vibe/artist/song per season
- requirements.txt # Python dependencies



---

## Technologies

- **Python**: Data cleaning and API enrichment
- **PostgreSQL**: SQL-based data modeling
- **Spotify API**: Metadata (track/artist IDs and genres)
- **Streamlit**: MVP dashboard
- **Figma**: UI/UX prototypes for future interactive redesign
- **React (Planned)**: Frontend for interactive views
- **Airflow (Planned)**: Scheduled ETL pipeline
- **dbt (Planned)**: Modular SQL transformation

---
## Getting Your Spotify Data

To use this app with your own listening history, you'll first need to download your data from Spotify.

### How to Download Your Spotify Streaming Data:

1. **Log into Spotify**:  
   Visit [https://www.spotify.com/account/privacy](https://www.spotify.com/account/privacy) and log into your account.

2. **Request Your Data**:  
   Scroll to the **"Download your data"** section. Select “Extended Streaming History” and submit your request.

3. **Wait for the Email**:  
   Spotify will email you a download link within a few days. The data will be provided in a **ZIP file** with **JSON files** inside.

4. **Extract and Convert**:  
   Once you receive the data, extract the ZIP file and locate the `StreamingHistory*.json` files. Convert these to CSV for this project.


## Setup Instructions

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/SpotifyVibeCatcher.git
   cd SpotifyVibeCatcher
2. Install dependencies:
   ```bash
    pip install -r requirements.txt

3. Add your Spotify API credentials in:
    - generateIDs.py
    - spotifygenre.py
4. Run transformation scripts:
- python TranformTime.py
- python generateIDs.py
- python spotifygenre.py

5. Run the SQL scripts in your PostgreSQL:
- setVibePerArtist.sql
- getVibePerHour.sql
- getVibePerDay.sql
- getVibePerSeason.sql

6. Launch the dashboard:
```bash
   streamlit run app.py
## Demo
https://drive.google.com/file/d/1yr-ucQopr27E6loqGThgFDaARMDgLwwz/view?usp=sharing

