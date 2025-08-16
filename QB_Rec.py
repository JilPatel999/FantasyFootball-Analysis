import pandas as pd
import ssl

'''
Getting top 5 QB recommendation
'''

# ---- Fixes SSL issue ----
ssl._create_default_https_context = ssl._create_unverified_context

# ---- coefficients from regression analysis----
coef = {
    'Cmp': 0.0214,
    'Att': -0.0170,
    'Pass_Yds': 0.0001,
    'Pass_TD': 0.2814,
    'INT': -0.1579,
    'Rush_Att': -0.0129,
    'Rush_Yds': 0.0062,
    'Rush_TD': 0.4140
}
intercept = 11.2901

# ---- Function to scrape PFR table ----
def scrape_pfr_table(url):
    df = pd.read_html(url)[0]  # read first table

    # If multi-level header, drop the top
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(0)

    if 'Rk' in df.columns:
        df = df[df['Rk'] != 'Rk']
        df.drop(columns=['Rk'], inplace=True, errors='ignore')

    df = df.drop_duplicates(subset=['Player'])

    return df

# ---- Year to pull ----
year = 2024

# ---- Scraping passing and rushing ----
passing_url = f"https://www.pro-football-reference.com/years/{year}/passing.htm"
rushing_url = f"https://www.pro-football-reference.com/years/{year}/rushing.htm"

passing_df = scrape_pfr_table(passing_url)
rushing_df = scrape_pfr_table(rushing_url)

if 'Pos' in passing_df.columns:
    passing_df = passing_df[passing_df['Pos'] == 'QB']


# Keep only relevant columns
passing_df = passing_df[['Player', 'Cmp', 'Att', 'Yds', 'TD', 'Int']]
passing_df.rename(columns={'Yds': 'Pass_Yds', 'TD': 'Pass_TD', 'Int': 'INT'}, inplace=True)

rushing_df = rushing_df[['Player', 'Att', 'Yds', 'TD']]
rushing_df.rename(columns={'Att': 'Rush_Att', 'Yds': 'Rush_Yds', 'TD': 'Rush_TD'}, inplace=True)

# ---- Merge on Player name ----
merged = pd.merge(passing_df, rushing_df, on='Player', how='inner')

# Convert all stat columns to numeric
for col in merged.columns:
    if col != 'Player':
        merged[col] = pd.to_numeric(merged[col], errors='coerce')

# ---- Calculate predicted Fantasy Points ----
merged['Predicted_Fantasy_PPG'] = (
    intercept
    + coef['Cmp'] * merged['Cmp']
    + coef['Att'] * merged['Att']  # Passing Attempts
    + coef['Pass_Yds'] * merged['Pass_Yds']
    + coef['Pass_TD'] * merged['Pass_TD']
    + coef['INT'] * merged['INT']
    + coef['Rush_Att'] * merged['Rush_Att']
    + coef['Rush_Yds'] * merged['Rush_Yds']
    + coef['Rush_TD'] * merged['Rush_TD']
)

recommendations = merged.sort_values(by='Predicted_Fantasy_PPG', ascending=False).head(10)

print("\nTop 10 QB Recommendations:")
print(recommendations[['Player', 'Predicted_Fantasy_PPG']])

