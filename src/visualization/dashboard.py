import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def get_launch_data_from_postgres():
    conn = psycopg2.connect(
        dbname="spacex_db",
        user="space_user",
        password="space_pass",
        host="postgres",
        port=5432
    )

    query = """
        SELECT name, date_utc, success, rocket
        FROM launches
        ORDER BY date_utc;
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    # Parse datetime
    df["date_utc"] = pd.to_datetime(df["date_utc"])
    return df


def visualize_launches(df: pd.DataFrame):
    sns.set(style="whitegrid")

    # 1. Success/failure over time
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x="date_utc", y="name", hue="success", palette="coolwarm")
    plt.title("SpaceX Launches Over Time (Success vs Failure)")
    plt.xlabel("Date")
    plt.ylabel("Mission Name")
    plt.tight_layout()
    plt.show()

    # 2. Launches by rocket
    plt.figure(figsize=(8, 5))
    sns.countplot(data=df, y="rocket", hue="success", palette="muted")
    plt.title("Launch Count by Rocket")
    plt.xlabel("Number of Launches")
    plt.ylabel("Rocket")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    df = get_launch_data_from_postgres()
    if not df.empty:
        visualize_launches(df)
    else:
        print("No launch data found in the database.")
