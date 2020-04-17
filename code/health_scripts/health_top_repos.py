import sys
import io
from contextlib import redirect_stdout
from common_functions import augur_db_connect, get_repo_info, get_dates, get_overall_risk
from common_functions import sustain_prs_by_repo, contributor_risk, response_time, activity_release, repo_api_call
from top_repos_common import get_commits_by_repo

six_months = 180  # Default to one year of data
year = 365   # Default to one year of data

engine = augur_db_connect()

# prepare csv file and write header row

try:
    csv_output = open('output/a_risk_assessment.csv', 'w')
    csv_output.write('repo_path,repo_name,commits,is_fork,overall_risk,sustain_risk,sustain_risk_num,contrib_risk,contrib_risk_num,response_risk,response_risk_num,release_risk,release_risk_num\n')
except:
    print('Could not write to csv file. Exiting')
    sys.exit(1)

start_date, end_date = get_dates(year)
six_start_date, six_end_date = get_dates(six_months)

commit_threshold = 100 # should be 100, 1500 for testing

repo_list_commits = get_commits_by_repo(six_start_date, six_end_date, engine)

top = repo_list_commits.loc[repo_list_commits['count'] > commit_threshold]

for index, repo in top.iterrows():

    repo_id = repo['repo_id']
    repo_name = repo['repo_name']
    repo_path = repo['repo_path']
    org_name = repo_path[11:(len(repo_path)-1)]

    print("Processing:", org_name, repo_name, repo_path, repo_id, repo['count'])

    repo_api = repo_api_call(repo_name, org_name) 
    is_fork = repo_api.fork

    repo_info = repo_path + ',' + repo_name + ',' + str(repo['count']) + ',' + str(is_fork) + ','
    csv_output.write(repo_info)

    try:
        # Only gather data from repos that aren't forks
        if is_fork == False:
            # gather data but suppress printing from these calls
            suppress = io.StringIO()
            with redirect_stdout(suppress):
                sustain_risk_num, sustain_risk = sustain_prs_by_repo(repo_id, repo_name, org_name, start_date, end_date, engine)
                contrib_risk_num, contrib_risk = contributor_risk(repo_id, repo_name, org_name, start_date, end_date, engine)
                response_risk_num, response_risk = response_time(repo_id, repo_name, org_name, start_date, end_date, engine)
                release_risk_num, release_risk = activity_release(repo_name, org_name, start_date, end_date, repo_api)

            overall_risk = get_overall_risk(sustain_risk, contrib_risk, response_risk, release_risk)
        
            # write data to csv file
            risk_info = overall_risk + ',' + sustain_risk + ',' + str(sustain_risk_num) + ',' + contrib_risk + ',' + str(contrib_risk_num) + ',' + response_risk + ',' + str(response_risk_num) + ',' + release_risk  + ',' + str(release_risk_num) + '\n'
            csv_output.write(risk_info)
        else:
            csv_output.write(',,,,,,,\n')

    except:
        csv_output.write(',,,,,,,\n')



