import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import matplotlib.pyplot as plt
import statsmodels.api as sm

def scrape_qb_stats(year):
    url = f"https://www.pro-football-reference.com/years/{year}/passing.htm"
    response = requests.get(url)
    soup = bs(response.content, 'html.parser')

    table = soup.find('table', {'id': 'passing'})
    df = pd.read_html(str(table))[0]

    df = df[df['Player'] != 'Player'].copy()

    df['Year'] = year

    df.reset_index(drop=True, inplace=True)

    return df

years = [2020, 2021, 2022, 2023, 2024]
all_seasons = pd.concat([scrape_qb_stats(y) for y in years], ignore_index=True)

'''
(Code for checking if scrapped data is correct)
print(all_seasons.head())
print(all_seasons.columns.tolist())
'''

columns_to_keep = ['Player', 'Year', 'Team', 'G', 'GS', 'Cmp', 'Att', 'Yds', 'TD', 'Int',
                   'Rate', 'Sk', 'Yds.1']
all_seasons = all_seasons[columns_to_keep]

all_seasons.rename(columns={
    'Yds': 'Pass_Yds',
    'TD': 'Pass_TD',
    'Int': 'INT',
    'Yds.1': 'Sack_Yds'
}, inplace=True)

stat_cols = ['G', 'GS', 'Cmp', 'Att', 'Pass_Yds', 'Pass_TD', 'INT',
             'Rate', 'Sk', 'Sack_Yds']
for col in stat_cols:
    all_seasons[col] = pd.to_numeric(all_seasons[col], errors='coerce')

all_seasons = all_seasons[all_seasons['Att'] > 50]
all_seasons.dropna(subset=['Pass_Yds', 'Pass_TD', 'INT'], inplace=True)

def scrape_qb_rushing(year):
    url = f'https://www.pro-football-reference.com/years/{year}/rushing.htm'
    res = requests.get(url)
    soup = bs(res.content, 'html.parser')

    table = soup.find('table', {'id': 'rushing'})

    df = pd.read_html(str(table))[0]

    # Fix header rows and drop repeated headers
    df.columns = df.columns.droplevel(0) if isinstance(df.columns, pd.MultiIndex) else df.columns
    df = df[df['Player'] != 'Player']  # drop repeated headers in table

    df['Year'] = year

    df = df[df['Pos'] == 'QB']

    return df

rushing_df = pd.concat([scrape_qb_rushing(y) for y in [2020, 2021, 2022, 2023, 2024]], ignore_index=True)

qb_rushing_df = rushing_df[rushing_df['Pos'] == 'QB']

qb_rushing_df = qb_rushing_df[['Player', 'Year', 'Att', 'Yds', 'TD']]
qb_rushing_df.rename(columns={
    'Att': 'Rush_Att',
    'Yds': 'Rush_Yds',
    'TD': 'Rush_TD'
}, inplace=True)

qb_rushing_df[['Rush_Att', 'Rush_Yds', 'Rush_TD']] = qb_rushing_df[['Rush_Att', 'Rush_Yds', 'Rush_TD']].apply(pd.to_numeric, errors='coerce')

## Left join merging with rushing and passing stats
merged_df = pd.merge(all_seasons, qb_rushing_df, on=['Player', 'Year'], how='left')

merged_df[['Rush_Att', 'Rush_Yds', 'Rush_TD']] = merged_df[['Rush_Att', 'Rush_Yds', 'Rush_TD']].fillna(0)

merged_df['Fantasy_Pts'] = (
    (merged_df['Pass_Yds'] / 25) +
    (merged_df['Pass_TD'] * 4) -
    (merged_df['INT'] * 2) +
    (merged_df['Rush_Yds'] / 10) +
    (merged_df['Rush_TD'] * 6)
)


rookie_dict = {
    2020: ['Joe Burrow', 'Justin Herbert', 'Tua Tagovailoa', 'Jalen Hurts'],
    2021: ['Trevor Lawrence', 'Zach Wilson', 'Trey Lance', 'Justin Fields', 'Mac Jones', 'Davis Mills'],
    2022: ['Kenny Pickett', 'Brock Purdy', 'Desmond Ridder', 'Malik Willis', 'Sam Howell'],
    2023: ['C.J. Stroud', 'Bryce Young', 'Anthony Richardson', 'Will Levis', "Aidan O'Connell"],
    2024: ['Caleb Williams', 'Jayden Daniels', 'Drake Maye', 'Bo Nix', 'Michael Penix Jr.']
}

# Add rookie flag using the dictionary (more accurate than Num_Seasons)
merged_df['Is_Rookie'] = merged_df.apply(
    lambda row: 1 if row['Player'] in rookie_dict.get(row['Year'], []) else 0, axis=1
)

# Begin cleaning
columns_to_drop = ['Rk', 'QBrec', 'QBR', 'Sk', 'Yds', 'Att.1', 'Yds.2', 'TD.1', 'Lng', 'Fmb']
merged_df.drop(columns=[col for col in columns_to_drop if col in merged_df.columns], inplace=True)

merged_df.fillna(0, inplace=True)
merged_df['Team'] = merged_df['Team'].astype(str)
merged_df['Player'] = merged_df['Player'].astype(str)

merged_df['Fantasy_PPG'] = merged_df['Fantasy_Pts'] / merged_df['GS']
merged_df = merged_df[merged_df['GS'] >= 8]


cols = ['Player', 'Year', 'Team', 'G', 'Fantasy_Pts', 'Fantasy_PPG', 'Is_Rookie'] + \
       [col for col in merged_df.columns if col not in ['Player', 'Year', 'Team', 'G', 'Fantasy_Pts', 'Fantasy_PPG', 'Is_Rookie']]
merged_df = merged_df[cols]

#---------------------------------------------------------------------------------------------------------------------------------------------
'''CREATING CHARTS FOR ANALYSIS'''

'''
Chart 1: Average QB Fantasy PPG per year 
Creating a trend analysis by grouping data by the Year to get avg fantasy points per game. 
'''

'''Avg fantasy ppg by year'''

trend_df = merged_df.groupby('Year')['Fantasy_PPG'].mean().reset_index()

plt.figure(figsize=(8,5))
fig, ax = plt.subplots()


fig.patch.set_facecolor('whitesmoke')
ax.set_facecolor('whitesmoke')


ax.plot(trend_df['Year'], trend_df['Fantasy_PPG'], marker='o')


ax.grid(False)

ax.set_xticks(trend_df['Year'])
ax.set_xticklabels(trend_df['Year'].astype(int))


ax.set_title('Average QB Fantasy Points per Game Yearly Trend (8 Games Started Min)')
ax.set_xlabel('Year')
ax.set_ylabel('Fantasy Points per Game')

plt.show()

#---------------------------------------------------------------------------------------------------------------------------------------------

''' 
Chart 2: Rookies vs Non-Rookies graph
This is done to see if there is learning curve for rookies, or do they come straight into the league
and perform
'''

# Calculate average Fantasy_PPG for rookies and non-rookies
avg_ppg = merged_df.groupby('Is_Rookie')['Fantasy_PPG'].mean().reset_index()
avg_ppg['Is_Rookie'] = avg_ppg['Is_Rookie'].map({0: 'Non-Rookie', 1: 'Rookie'})

plt.figure(figsize=(6, 4))
bars = plt.bar(avg_ppg['Is_Rookie'], avg_ppg['Fantasy_PPG'], color=['steelblue', 'orange'])
plt.title('Average Fantasy PPG: Rookies vs Non-Rookies (8 Games Started Min)', fontsize=14)
plt.ylabel('Fantasy PPG')
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.gca().set_facecolor('whitesmoke')  # Background color
plt.grid(False)  # Remove grid lines

# Adding value labels on bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.2f}',
             ha='center', va='bottom', fontsize=10)

plt.show()

#---------------------------------------------------------------------------------------------------------------------------------------------

'''Regression Analysis'''
X = merged_df[['Cmp', 'Att', 'Pass_Yds', 'Pass_TD', 'INT',
               'Rush_Att', 'Rush_Yds', 'Rush_TD']]

X = sm.add_constant(X)

y = merged_df['Fantasy_PPG']

model = sm.OLS(y, X).fit()

print(model.summary())



'''Making regression coefficients graph based on the results'''


coef_df = pd.DataFrame({
    'stat': ['Cmp', 'Att', 'Pass_Yds', 'Pass_TD', 'INT', 'Rush_Att', 'Rush_Yds', 'Rush_TD'],
    'coef': [0.0214, -0.0170, 0.0001, 0.2814, -0.1579, -0.0129, 0.0062, 0.4140]
})
colors = ['green' if c > 0 else 'red' for c in coef_df['coef']]

coef_df = coef_df.reindex(coef_df['coef'].abs().sort_values(ascending=True).index)

coef_df['color'] = coef_df['coef'].apply(lambda x: 'green' if x > 0 else 'red')

plt.figure(figsize=(8, 5))
plt.barh(coef_df['stat'], coef_df['coef'], color=coef_df['color'])
plt.xlabel('Impact on Fantasy_PPG')
plt.ylabel('Stat')
plt.title('Impact of Each Stat on Fantasy Points Per Game')
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.grid(False)
plt.show()




