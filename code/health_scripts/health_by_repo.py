### Usage:
###    $ python3 health_by_repo.py github_organization_name repository_name
### Example:
###    $ python3 health_by_repo.py vmware-tanzu velero

from common_functions import augur_db_connect, get_repo_info, get_dates, get_overall_risk, write_overall_risk_file
from common_functions import contributor_risk, response_time, activity_release, repo_api_call
from common_functions import fork_archive, sustain_prs_by_repo_graph

days = 365 # Default to one year of data

engine = augur_db_connect()

repo_id, org_name, repo_name = get_repo_info(engine)

start_date, end_date = get_dates(days)

is_forked, is_archived = fork_archive(repo_name, org_name, engine)
print('Forked:', str(is_forked), '\nArchived:', str(is_archived))

repo_api = repo_api_call(repo_name, org_name)

release_risk_num, release_risk = activity_release(repo_name, org_name, start_date, end_date, repo_api)

sustain_risk_num, sustain_risk = sustain_prs_by_repo_graph(repo_id, repo_name, org_name, start_date, end_date, engine)

contrib_risk_num, contrib_risk = contributor_risk(repo_id, repo_name, org_name, start_date, end_date, engine)

response_risk_num, response_risk = response_time(repo_id, repo_name, org_name, start_date, end_date, engine)

overall_risk = get_overall_risk(sustain_risk, contrib_risk, response_risk, release_risk)

write_overall_risk_file(repo_name, org_name, overall_risk, sustain_risk, contrib_risk, response_risk, release_risk)

print("Overall Assessment:", overall_risk)
