# app.py
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Set Streamlit page config
st.set_page_config(page_title="What Do I Listen to When?", layout="wide")

st.title("🎧 What Do I Listen to When?")
st.markdown("Explore your top vibes, artists, and songs by hour, day, and season.")

# Load data
hour_df = pd.read_csv("data/vibeperhour.csv")
day_df = pd.read_csv("data/vibeperday.csv")
season_df = pd.read_csv("data/vibeperseason.csv")

# Format hour for correct display order
hour_df['time_display'] = pd.Categorical(
    hour_df['time_display'],
    categories=[
        f"{h}:00 AM" if h < 12 else f"{h-12 if h > 12 else 12}:00 PM"
        for h in range(24)
    ],
    ordered=True
)

# Tabs for each view
tab1, tab2, tab3 = st.tabs(["🕐 By Hour", "📆 By Day", "🍂 By Season"])

with tab1:
    st.subheader("Vibe Distribution by Hour")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=hour_df, x="time_display", y="avg_vibe_plays", hue="dominant_vibe", ax=ax)
    ax.set_xlabel("Hour")
    ax.set_ylabel("Avg Plays")
    ax.set_title("Most Listened Vibe by Hour")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    st.markdown("#### Top Artist and Song Each Hour")
    st.dataframe(hour_df[["time_display", "top_artist", "top_song"]])

with tab2:
    st.subheader("Vibe Distribution by Day")
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.barplot(data=day_df, x="day_of_week", y="avg_vibe_plays", hue="dominant_vibe", ax=ax2)
    ax2.set_title("Most Listened Vibe by Day")
    st.pyplot(fig2)

    st.markdown("#### Top Artist and Song Each Day")
    st.dataframe(day_df[["day_of_week", "top_artist", "top_song"]])

with tab3:
    st.subheader("Vibe Distribution by Season")
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    sns.barplot(data=season_df, x="season", y="avg_vibe_plays", hue="dominant_vibe", ax=ax3)
    ax3.set_title("Most Listened Vibe by Season")
    st.pyplot(fig3)

    st.markdown("#### Top Artist and Song Each Season")
    st.dataframe(season_df[["season", "top_artist", "top_song"]])
