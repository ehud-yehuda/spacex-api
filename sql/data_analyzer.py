import sys
import os

# Add parent directory and src folder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from db_server import dBServer
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd

db_reader = dBServer()

def plot_launches_per_site(df: pd.DataFrame, pdf=None):
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(14, 8))
    sns.barplot(y='launch_site', x='number_of_launches', data=df, palette='viridis')
    plt.title('Number of Launches per Launch Site')
    plt.xlabel('Number of Launches')
    plt.ylabel('Launch Site')
    plt.tight_layout()
    if pdf:
        pdf.savefig()
        plt.close()
    else:
        plt.show()

def plot_launch_delays(df: pd.DataFrame, pdf=None):
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(12, 6))
    sns.lineplot(x='launch_year', y='avg_delay_hours', data=df, marker="o", label="Average Delay (Hours)")
    sns.lineplot(x='launch_year', y='max_delay_hours', data=df, marker="o", label="Maximum Delay (Hours)")
    plt.title('Average and Maximum Launch Delays Over Years')
    plt.xlabel('Year')
    plt.ylabel('Delay (Hours)')
    plt.legend()
    plt.xticks(df['launch_year'].astype(int), rotation=45)
    plt.tight_layout()
    if pdf:
        pdf.savefig()
        plt.close()
    else:
        plt.show()

def plot_success_rate(df: pd.DataFrame, pdf=None):
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(12, 6))
    sns.lineplot(x='launch_year', y='success_rate_percentage', data=df, marker="o")
    plt.title('SpaceX Launch Success Rate Over Years')
    plt.xlabel('Year')
    plt.ylabel('Success Rate (%)')
    plt.xticks(df['launch_year'].astype(int), rotation=45)
    plt.tight_layout()
    if pdf:
        pdf.savefig()
        plt.close()
    else:
        plt.show()

def plot_top_heavy_launches(df: pd.DataFrame, pdf=None):
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(12, 6))
    sns.barplot(y='launch_id', x='total_payload_mass', data=df, palette='mako')
    plt.title('Top 5 Launches by Total Payload Mass')
    plt.xlabel('Total Payload Mass (kg)')
    plt.ylabel('Launch Name')
    plt.tight_layout()
    if pdf:
        pdf.savefig()
        plt.close()
    else:
        plt.show()

def analyze_launch_success_rate_over_years(fetch_only=False):
    query = """
    SELECT
        EXTRACT(YEAR FROM date_utc) AS launch_year,
        COUNT(*) AS total_launches,
        SUM(CASE WHEN success = TRUE THEN 1 ELSE 0 END) AS successful_launches,
        ROUND( (SUM(CASE WHEN success = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2 ) AS success_rate_percentage
    FROM
        launches
    GROUP BY
        launch_year
    ORDER BY
        launch_year;
    """
    df = db_reader.read_query_to_dataframe(query)
    if fetch_only:
        return df
    if not df.empty:
        print(df)
        plot_success_rate(df)

def analyze_top_heavy_launches(fetch_only=False):
    query = """
    SELECT
        data_as_json->>'launch_id_updated' AS launch_id,
        last_updated_launch_date,
        (data_as_json->>'payload_mass')::numeric AS total_payload_mass
    FROM
        aggregate_data_table
    ORDER BY
        total_payload_mass DESC
    LIMIT 5;
    """
    df = db_reader.read_query_to_dataframe(query)
    if fetch_only:
        return df

    if not df.empty:
        print(df)
        plot_top_heavy_launches(df)

def analyze_launch_delays_over_years(fetch_only=False):
    query = """
    SELECT
        EXTRACT(YEAR FROM last_updated_launch_date) AS launch_year,
        ROUND((AVG((data_as_json->>'delay_time')::float) / 3600)::numeric, 2) AS avg_delay_hours,
        ROUND((MAX((data_as_json->>'delay_time')::float) / 3600)::numeric, 2) AS max_delay_hours
    FROM
        aggregate_data_table
    GROUP BY
        launch_year
    ORDER BY
        launch_year;
    """
    df = db_reader.read_query_to_dataframe(query)
    if fetch_only:
        return df
    if not df.empty:
        print(df)
        plot_launch_delays(df)

def analyze_launches_per_site(fetch_only=False):
    query = """
    SELECT
        l.data_as_json->>'launchpad' AS launch_site,
        COUNT(*) AS number_of_launches,
        ROUND((AVG((agg.data_as_json->>'payload_mass')::float))::numeric, 2) AS avg_payload_mass_kg
    FROM
        aggregate_data_table agg
    JOIN
        launches l ON (l.id = (agg.data_as_json->>'launch_id_updated'))
    WHERE
        (agg.data_as_json->>'payload_mass') IS NOT NULL
    GROUP BY
        launch_site
    ORDER BY
        number_of_launches DESC;
    """
    df = db_reader.read_query_to_dataframe(query)
    if fetch_only:
        return df
    if not df.empty:
        print(df)
        plot_launches_per_site(df)

def create_pdf_report(filename="SpaceX_Analysis_Report.pdf"):
    with PdfPages(filename) as pdf:
        # Success Rate
        df1 = analyze_launch_success_rate_over_years(fetch_only=True)
        if not df1.empty:
            plot_success_rate(df1, pdf=pdf)

        # Heaviest Launches
        df2 = analyze_top_heavy_launches(fetch_only=True)
        if not df2.empty:
            plot_top_heavy_launches(df2, pdf=pdf)

        # Launch Delays
        df3 = analyze_launch_delays_over_years(fetch_only=True)
        if not df3.empty:
            plot_launch_delays(df3, pdf=pdf)

        # Launches per Site
        df4 = analyze_launches_per_site(fetch_only=True)
        if not df4.empty:
            plot_launches_per_site(df4, pdf=pdf)

        print(f"✅ PDF report generated successfully: {filename}")

def main():
    create_pdf_report()


if __name__ == "__main__":
    main()