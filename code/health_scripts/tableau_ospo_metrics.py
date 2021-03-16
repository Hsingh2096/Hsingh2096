#OBSOLETE - This script has been moved to the Jupyter Notebook: OSPO_Project_Health_Data_Tableau.ipynb


from common_functions import augur_db_connect, get_dates, get_commits_by_repo
from common_functions import repo_api_call, fork_archive
from tableau_functions import sustain_prs_by_repo_tableau, contributor_risk_tableau, response_time_tableau, activity_release_tableau

six_months = 180  # Default to one year of data
year = 365   # Default to one year of data

engine = augur_db_connect()

start_date, end_date = get_dates(year)
six_start_date, six_end_date = get_dates(six_months)

commit_threshold = 60 # 90 but use 1500 for testing

repo_list_commits = get_commits_by_repo(six_start_date, six_end_date, engine)

top = repo_list_commits.loc[repo_list_commits['count'] > commit_threshold]

# Testing - Delete this line later
i = 0

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

    # Only gather data from repos that aren't forks or archived
    if is_fork == False and is_archived == False:
        sustain_prs_by_repo_tableau(repo_id, repo_name, org_name, start_date, end_date, engine)
        contributor_risk_tableau(repo_id, repo_name, org_name, start_date, end_date, engine)
        response_time_tableau(repo_id, repo_name, org_name, start_date, end_date, engine)
        activity_release_tableau(repo_name, org_name, start_date, end_date, repo_api)

    # Testing - Delete these lines later
    if i > 2:
        break
    else:
       i+=1

