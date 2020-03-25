### Usage:
###    $ python3 health_by_repo.py github_organization_name repository_name
### Example:
###    $ python3 health_by_repo.py vmware-tanzu velero

from common_functions import augur_db_connect, get_repo_info, get_dates
from common_functions import sustain_prs_by_repo, contributor_risk, response_time

days = 365 # Default to one year of data

engine = augur_db_connect()

repo_id, org_name, repo_name = get_repo_info(engine)

start_date, end_date = get_dates(days)

sustain_risk_num, sustain_risk = sustain_prs_by_repo(repo_id, repo_name, start_date, end_date, engine)

contrib_risk_num, contrib_risk = contributor_risk(repo_id, repo_name, start_date, end_date, engine)

response_risk_num, response_risk = response_time(repo_id, repo_name, start_date, end_date, engine)