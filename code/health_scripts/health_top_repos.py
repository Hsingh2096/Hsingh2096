import sys
import io
from contextlib import redirect_stdout
from common_functions import augur_db_connect, get_dates, get_overall_risk, write_overall_risk_file, get_commits_by_repo
from common_functions import sustain_prs_by_repo_graph, contributor_risk_graph, response_time_graph, activity_release_graph
from common_functions import repo_api_call, fork_archive

six_months = 180  # Default to one year of data
year = 365   # Default to one year of data

engine = augur_db_connect()

# prepare csv file and write header row

try:
    csv_output = open('output/a_risk_assessment.csv', 'w')
    csv_output.write('repo_path,repo_name,commits,overall_risk,sustain_risk,sustain_risk_num,contrib_risk,contrib_risk_num,response_risk,response_risk_num,release_risk,release_risk_num\n')
except:
    print('Could not write to csv file. Exiting')
    sys.exit(1)

start_date, end_date = get_dates(year)
six_start_date, six_end_date = get_dates(six_months)

commit_threshold = 60 # 90 but use 1500 for testing

repo_list_commits = get_commits_by_repo(six_start_date, six_end_date, engine)

top = repo_list_commits.loc[repo_list_commits['count'] > commit_threshold]

i = 0  ##### testing

for index, repo in top.iterrows():

    repo_id = repo['repo_id']
    repo_name = repo['repo_name']
    repo_path = repo['repo_path']
    org_name = repo_path[11:(len(repo_path)-1)]

    print('Processing:', org_name, repo_name, repo_path, repo_id, repo['count'])

    try:
        repo_api = repo_api_call(repo_name, org_name)
    except:
        print('Cannot process API calls for:', org_name, repo_name, repo_path, repo_id)

    is_fork, is_archived = fork_archive(repo_name, org_name, engine)

    try:
        # Only gather data from repos that aren't forks or archived
        if is_fork == False and is_archived == False:
            repo_info = repo_path + ',' + repo_name + ',' + str(repo['count']) + ','
            csv_output.write(repo_info)

            # gather data but suppress printing from these calls
            suppress = io.StringIO()
            with redirect_stdout(suppress):
                sustain_risk_num, sustain_risk = sustain_prs_by_repo_graph(repo_id, repo_name, org_name, start_date, end_date, engine)
                contrib_risk_num, contrib_risk = contributor_risk_graph(repo_id, repo_name, org_name, start_date, end_date, engine)
                response_risk_num, response_risk = response_time_graph(repo_id, repo_name, org_name, start_date, end_date, engine)
                release_risk_num, release_risk = activity_release_graph(repo_name, org_name, start_date, end_date, repo_api)

            overall_risk = get_overall_risk(sustain_risk, contrib_risk, response_risk, release_risk)
            write_overall_risk_file(repo_name, org_name, overall_risk, sustain_risk, contrib_risk, response_risk, release_risk)

 
            # write data to csv file
            risk_info = overall_risk + ',' + sustain_risk + ',' + str(sustain_risk_num) + ',' + contrib_risk + ',' + str(contrib_risk_num) + ',' + response_risk + ',' + str(response_risk_num) + ',' + release_risk  + ',' + str(release_risk_num) + '\n'
            csv_output.write(risk_info)

    except:
        csv_output.write('DATA ERROR,\n')

    # Testing - Delete these lines later
    if i > 2:
        break
    else:
       i+=1    
