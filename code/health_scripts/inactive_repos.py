import sys
import pandas as pd
from common_functions import augur_db_connect, get_repo_info, get_dates

engine = augur_db_connect()

# prepare csv file and write header row

try:
    csv_output = open('output/a_repo_activity.csv', 'w')
    csv_output.write('repo_link,org,repo_name,repo_id,last_updated,last_commiter,most_commits,most_num,second_most,second_num\n')
except:
    print('Could not write to csv file. Exiting')
    sys.exit(1)

# Put all commits into a dataframe

print('\nRunning database query - this step takes several minutes.')

all_commits = pd.DataFrame()
all_commits_query = f"""
        SELECT DISTINCT(commits.cmt_commit_hash), repo.repo_id, repo.repo_name, repo.repo_path, 
            commits.cmt_author_email, commits.cmt_author_timestamp from repo, commits
        WHERE 
            repo.repo_id = commits.repo_id
        GROUP BY repo.repo_id, commits.cmt_commit_hash, commits.cmt_author_email, commits.cmt_author_timestamp
        ORDER BY repo.repo_id;
        """
all_commits = pd.read_sql_query(all_commits_query, con=engine)

# Group commits by repo with latest timestamp
by_repo = all_commits.loc[all_commits.groupby('repo_id').cmt_author_timestamp.idxmax()].sort_values('cmt_author_timestamp')

# Create list of donated orgs to exclude

exclude_list = ["projectcontour", "goharbor"]

# This gives us the top contributors per repo for the csv file 

print('Writing data to CSV file')
i=0
for index, row in by_repo.iterrows():
    repo_link = row.repo_path + row.repo_name
    org = row.repo_path.split("/")[1]

    if org not in exclude_list:
        basic_info = repo_link + ',' + org + ',' + row.repo_name + ',' + str(row.repo_id) + ',' + str(row.cmt_author_timestamp) + ',' + row.cmt_author_email + ','
        csv_output.write(basic_info)
    
        top_contribs = all_commits.loc[all_commits['repo_id'] == row.repo_id].cmt_author_email.value_counts()
        if len(top_contribs) > 1:
            committer_info = top_contribs.index[0] + ',' + str(top_contribs[0]) + ',' + top_contribs.index[1] + ',' + str(top_contribs[1]) + '\n'
        elif len(top_contribs) == 1:
            committer_info = top_contribs.index[0] + ',' + str(top_contribs[0]) + ',' + 'None' + ',' + 'None' + '\n'
        elif len(top_contribs) == 0:
            committer_info = 'None' + ',' + 'None' + ',' + 'None' + ',' + 'None' + '\n'
        csv_output.write(committer_info)

