# importing Libraries

import pandas as pd
import xlrd
import xlwt
import os
import sys

# -----------------------------------------------------------------------------------------------------------------------
# Selecting Parameters

team_predict = input('What team do you want to predict?  ')     # Team that you want to predict
ref_predict = input('What referee do you want to predict? ')     # Referee that you want to predict

# Select the time period where prior and likelihood are calculated. Data ranges from 2004 to 2019
prior_year_start = input('What should be the start of the Prior Period [choose between 2004 and 2018]  ')
prior_year_end = '2019'
like_year_start = '2004'
like_year_end = '2019'

# -----------------------------------------------------------------------------------------------------------------------
# Importing the Data

# Read Files
path = sys.path[0]+"\data"
files = os.listdir(path)

files_csv = [f for f in files if f[-3:] == 'csv']

files_df = pd.DataFrame()        # This dataframe will store data for the likelihood period
files_prior_df = pd.DataFrame()  # This dataframe will store data for the prior period
teams_year = {}

for f in files_csv:
    data = pd.read_csv(path+'\\'+f, encoding='cp1252', parse_dates=[1])
    data_home = data['HomeTeam'].unique().tolist()
    year = str(data['Date'].dt.to_period('Y')[0])
    teams_year[year] = data_home
    files_df = files_df.append(data)
    if int(str(data['Date'].dt.to_period('Y')[0])) in range(int(prior_year_start), int(prior_year_end)):
        files_prior_df = files_prior_df.append(data)

# Check if the Team participated during the prior period
count = 0

for i in range(int(prior_year_start), int(prior_year_end)):
    if team_predict in teams_year[str(i)]:
        count = count+1

if count == 0:
    print(f'{team_predict} did not participate in Premier League in the period {prior_year_start} to {prior_year_end}')
    sys.exit('Alter the input parameters and try again')

# -----------------------------------------------------------------------------------------------------------------------
# Data Pre Processing

# Select Columns
interesting_columns = ['HomeTeam', 'AwayTeam', 'FTR', 'Referee', 'Date']
games = files_df[interesting_columns]
games['Referee'] = games['Referee'].str.split().str.join(' ')
games.dropna(inplace=True)

teams = files_prior_df['HomeTeam'].unique().tolist()  # ALL TEAMS from the prior period
refs = games['Referee'].unique().tolist()             # ALL REFEREES from the likelihood period

# Group all games of all teams from prior period in a list: teams_refs
# teams_refs = [[Team1,[[Game1],[Game2],...[GameN]]], [Team2,[[Game1],[Game2],...[GameN]]], ..., [TeamN,Games]]

teams_refs = []

for i in teams:
    i_team_list = []
    for j in refs:
        i_team_j_ref = games[((games['HomeTeam'] == i) | (games['AwayTeam'] == i)) & (games['Referee'] == j)]
        i_team_j_ref_list = i_team_j_ref.values.tolist()
        for k in i_team_j_ref_list:
            i_team_list.append(k)
    teams_refs.append([i, i_team_list])

# -----------------------------------------------------------------------------------------------------------------------
# Create one DataFrame to include all final results: Teams, Prior, Likelihood
# for each team that contains the Prior of each team and the Likelihood for each referee for the specific team

#               [Prior]                     [Likelihood]
#   Team1   P(W) P(L) P(D)   Ref1   P(Ref1|W) P(Ref1|L) P(Ref1|D)
#                            Ref2   P(Ref2|W) P(Ref2|L) P(Ref2|D)
#                            ...
#                            RefN   P(RefN|W) P(RefN|L) P(RefN|D)
#   ...
#   ...
#   ...
#   TeamM   P(W) P(L) P(D)   Ref1   P(Ref1|W) P(Ref1|L) P(Ref1|D)
#                            Ref2   P(Ref2|W) P(Ref2|L) P(Ref2|D)
#                            ...
#                            RefN   P(RefN|W) P(RefN|L) P(RefN|D)

likelihood_columns = interesting_columns.copy()
likelihood_columns.append('Result')

teams_total = pd.DataFrame(index=teams, columns=['Prior', 'Likelihood'])  # DataFrame to include all final results


for team in range(len(teams)):
    for i in teams_refs[team][1]:
        if (((i[0] == teams_refs[team][0]) & (i[2] == 'H'))|((i[1] == teams_refs[team][0]) & (i[2] == 'A'))):
            i.append('WIN')
        elif ((i[2] == 'D')):
            i.append('DRAW')
        else:
            i.append('LOSS')

    team_df = pd.DataFrame(teams_refs[team][1], columns=likelihood_columns)[['Referee', 'Result', 'Date']]  # Intermidiate DF with team - referee results

    team_like = team_df.groupby('Referee')['Result'].apply(list).to_frame().reset_index()  # DF with likelihood for 1 team and for all referees
    team_like[['P(Ref|Win)', 'P(Ref|Loss)', 'P(Ref|Draw)']] = 0

    team_prior = pd.DataFrame(columns=[['P(Win)', 'P(Loss)', 'P(Draw)']], index=[0]) # Dataframe with Prior for the Team


# Calculating Prior
    team_prior.iloc[0]['P(Win)'] = float(team_df[(team_df['Date'] >= prior_year_start) & (team_df['Date'] <= prior_year_end)]['Result'].value_counts(normalize=True).loc['WIN'])
    team_prior.iloc[0]['P(Loss)'] = float(team_df[(team_df['Date'] >= prior_year_start) & (team_df['Date'] <= prior_year_end)]['Result'].value_counts(normalize=True).loc['LOSS'])
    team_prior.iloc[0]['P(Draw)'] = float(team_df[(team_df['Date'] >= prior_year_start) & (team_df['Date'] <= prior_year_end)]['Result'].value_counts(normalize=True).loc['DRAW'])

# Calculating Likelihood
    for j in range(len(team_like)):
        team_like['P(Ref|Win)'].iloc[j] = team_like['Result'].iloc[j].count('WIN') / len(team_like['Result'].iloc[j])
        team_like['P(Ref|Loss)'].iloc[j] = team_like['Result'].iloc[j].count('LOSS') / len(team_like['Result'].iloc[j])
        team_like['P(Ref|Draw)'].iloc[j] = team_like['Result'].iloc[j].count('DRAW') / len(team_like['Result'].iloc[j])

    team_like.drop(columns=['Result'], inplace=True)
    team_like.set_index('Referee', inplace=True, drop=True)

# Appending the Likelihood and the Prior to the teams_total dataframe
    teams_total.loc[teams[team]]['Likelihood'] = team_like
    teams_total.loc[teams[team]]['Prior'] = team_prior

# ----------------------------------------------------------------------------------------------------------------------
# Calculate the Posterior Probability for the specific Team and the specific Referee

# Print the Prior Probability of the selected Team
print(f'{team_predict} Prior Probability')
print(teams_total.loc[team_predict]['Prior'])
print('----------------------------------------------------')

# Print the likelihood of the selected Team with the selected Referee
print(f'{ref_predict} / {team_predict} Likelihood')
print(teams_total.loc[team_predict]['Likelihood'].loc[ref_predict])
print('----------------------------------------------------')

# Calculate the posterior probability
win = teams_total.loc[team_predict]['Prior'].iloc[0]['P(Win)'].values[0]*teams_total.loc[team_predict]['Likelihood'].loc[ref_predict].loc['P(Ref|Win)']
loss = teams_total.loc[team_predict]['Prior'].iloc[0]['P(Loss)'].values[0]*teams_total.loc[team_predict]['Likelihood'].loc[ref_predict].loc['P(Ref|Loss)']
draw = teams_total.loc[team_predict]['Prior'].iloc[0]['P(Draw)'].values[0]*teams_total.loc[team_predict]['Likelihood'].loc[ref_predict].loc['P(Ref|Draw)']

p_win = win/(win+loss+draw)
p_loss = loss/(win+loss+draw)
p_draw = draw/(win+loss+draw)

# Print the posterior probability
print(f'Posterior Probability: {team_predict} / {ref_predict}')
print('P(Win|Ref) = ', p_win)
print('P(Loss|Ref) = ', p_loss)
print('P(Draw|Ref) = ', p_draw)
