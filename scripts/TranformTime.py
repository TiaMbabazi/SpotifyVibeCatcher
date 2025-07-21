import pandas as pd
def transform():
    df = pd.read_csv("data/StreamingHistory_podcast_0.csv")
    df["endTime"] = pd.to_datetime(df["endTime"])
    df["hourlyTime"] = df["endTime"].dt.floor("H")
    print(df.head())
    df.to_csv("data/StreamingHistory_podcast_transformed.csv", index=False, date_format='%Y-%m-%d %H:%M:%S')



transform()
