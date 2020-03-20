### Usage:
###    $ python3 health_by_repo.py github_organization_name repository_name
### Example:
###    $ python3 health_by_repo.py vmware-tanzu velero

from common_functions import augur_db_connect, get_repo_info, get_dates, sustain_prs_by_repo, contributor_risk

days = 365 # Default to one year of data

engine = augur_db_connect()

repo_id, org_name, repo_name = get_repo_info(engine)

start_date, end_date = get_dates(days)

#sustain_prs_by_repo(repo_id, repo_name, start_date, end_date, engine)

contributor_risk(repo_id, repo_name, start_date, end_date, engine)

