from common_functions import augur_db_connect, get_repo_info, get_dates
from common_functions import sustain_prs_by_repo, contributor_risk, response_time
from top_repos_common import get_commits_by_repo

six_months = 180  # Default to one year of data
year = 365   # Default to one year of data

engine = augur_db_connect()

start_date, end_date = get_dates(year)
six_start_date, six_end_date = get_dates(six_months)
commit_threshold = 400

repo_list_commits = get_commits_by_repo(six_start_date, six_end_date, engine)

top = repo_list_commits.loc[repo_list_commits['count'] > commit_threshold]

forked_list = [27050, 27645, 26994]

for index, repo in top.iterrows():

    repo_id = repo['repo_id']
    repo_name = repo['repo_name']
    repo_path = repo['repo_path']

    print(repo_id, repo_name, repo_path, repo['count'])

    if repo_id not in forked_list:
        sustain_risk_num, sustain_risk = sustain_prs_by_repo(repo_id, repo_name, start_date, end_date, engine)
        contrib_risk_num, contrib_risk = contributor_risk(repo_id, repo_name, start_date, end_date, engine)
        response_risk_num, response_risk = response_time(repo_id, repo_name, start_date, end_date, engine)

#    print(repo_name, repo_path)
#    print('Sustain - keeps up with PRs:', sustain_risk, sustain_risk_num, 'months with > 10% of total PRs not closed in the past 6 months')
#    print('Contributor risk assessment:', contrib_risk, contrib_risk_num, 'people made the majority of commits last year')
#    print('Responsiveness to PRs: ', response_risk, response_risk_num, 'months with median response times > 1 day in the past 6 months')

