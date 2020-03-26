import sys
from common_functions import augur_db_connect, get_repo_info, get_dates
from common_functions import sustain_prs_by_repo, contributor_risk, response_time
from top_repos_common import get_commits_by_repo

six_months = 180  # Default to one year of data
year = 365   # Default to one year of data

engine = augur_db_connect()

# prepare csv file and write header row

try:
    csv_output = open('output/risk_assessment.csv', 'w')
    csv_output.write('repo_path,repo_name,repo_id,commits,overall_risk,sustain_risk,sustain_risk_num,contrib_risk,contrib_risk_num,response_risk,response_risk_num\n')
except:
    print('Could not write to csv file. Exiting')
    sys.exit(1)

start_date, end_date = get_dates(year)
six_start_date, six_end_date = get_dates(six_months)
commit_threshold = 0 # should be 50, 1000 for testing

repo_list_commits = get_commits_by_repo(six_start_date, six_end_date, engine)

top = repo_list_commits.loc[repo_list_commits['count'] > commit_threshold]

for index, repo in top.iterrows():

    repo_id = repo['repo_id']
    repo_name = repo['repo_name']
    repo_path = repo['repo_path']

    print(repo_id, repo_name, repo_path, repo['count'])

    repo_info = repo_path + ',' + repo_name + ',' + str(repo_id) + ',' + str(repo['count']) + ','
    csv_output.write(repo_info)

    try:
        # gather data
        sustain_risk_num, sustain_risk = sustain_prs_by_repo(repo_id, repo_name, start_date, end_date, engine)
        contrib_risk_num, contrib_risk = contributor_risk(repo_id, repo_name, start_date, end_date, engine)
        response_risk_num, response_risk = response_time(repo_id, repo_name, start_date, end_date, engine)

        # calculate overall risk score
        risk_count = [sustain_risk, contrib_risk, response_risk].count('AT RISK')
        if risk_count == 0:
            overall_risk = 'LOW RISK'
        elif (risk_count == 1 or risk_count == 2):
            overall_risk = 'MEDIUM RISK'
        elif risk_count == 3:
            overall_risk = 'HIGH RISK'
        
        print(overall_risk)
        
        # write data to csv file
        risk_info = overall_risk + ',' + sustain_risk + ',' + str(sustain_risk_num) + ',' + contrib_risk + ',' + str(contrib_risk_num) + ',' + response_risk + ',' + str(response_risk_num) + '\n'
        csv_output.write(risk_info)
    except:
        csv_output.write(',,,,,,\n')



