The Python Script Premier_League_Posterior.py will calculate 
the Posterior Probability for a team to win in its next match
(random opponent), given that the referee in their next match 
will be predetermined.

Moreover, there are two .txt files, ‘All_teams.txt’ and 
‘All_refs.txt’, which contain lists of all viable input options for 
the team and the referee.

When running the script, the .csv files in the data folder will
be accessed (Premier League data from 2014 to 2019) and the user 
should answer 3 questions in the cmd promt (correct input is needed):

- What is the team name? (see All_Teams.txt for potential answers)
- What is the referee name? (see ALL_Refs.txt for potential answers)
- When does the Prior period begin? (between 2014 and 2018)

The script will print:

- The Prior probability of the team to win/lose/draw
	P(Win), P(Loss), P(Draw)

- The Likelihood of the specific Referee for the 
team to win/lose/draw
	P(Ref|Win), P(Ref|Loss), P(Ref|Draw)

- The Posterior probability for the team to win, given
that the specific referee was selected for the next match
	P(Win|Ref), P(Loss|Ref), P(Draw|Ref)

- If the name of the selected team isn't included in the
championships of the selected prior period, the script is terminated

Requirements: 
1OS	0.1	0.1
numpy	1.19.2	1.19.4
pandas	1.1.3	1.1.4
pip	19.0.3	20.2.4
python-dateutil	2.8.1	2.8.1
pytz	2020.1	2020.4
setuptools	40.8.0	50.3.2
six	1.15.0	1.15.0
xlrd	1.2.0	1.2.0
xlwt	1.3.0	1.3.0