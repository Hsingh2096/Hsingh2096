import sys
import pandas as pd
from common_functions import augur_db_connect, get_repo_info, get_dates, repo_api_call, build_id_map

engine = augur_db_connect()

# Create a dictionary that maps email addresses to github ids
id_dict = build_id_map(engine)

# prepare csv file and write header row

try:
    csv_output = open('output/a_repo_activity.csv', 'w')
    csv_output.write('repo_link,org,repo_name,is_fork,is_archived,redirect,last_updated,last_commiter,last_github,most_commits,most_github,most_num,second_most,second_github,second_num\n')
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

exclude_list = ["projectcontour", "goharbor", "tern-tools"]

# This gives us the top contributors per repo for the csv file 

print('Writing data to CSV file')
i=0
for index, row in by_repo.iterrows():
    repo_link = row.repo_path + row.repo_name
    org = row.repo_path.split("/")[1]

    if org not in exclude_list:
        try:
            repo_api = repo_api_call(row.repo_name, org)
            is_fork = repo_api.fork
            is_archived = repo_api.archived

            full_name = org + '/' + row.repo_name
            api_name = repo_api.full_name
            if full_name.lower() == api_name.lower():
                redirect = False
            else:
                redirect = api_name

        except:
            is_fork = 'API ERROR'
            is_archive = 'API ERROR'
            redirect = 'API ERROR'

        try:
            last_github = str(id_dict[row.cmt_author_email][0])
        except:
            last_github = 'None'
#        print(row.cmt_author_email, last_github)
        basic_info = repo_link + ',' + org + ',' + row.repo_name + ',' + str(is_fork) + ',' + str(is_archived) + ',' + str(redirect) + ',' + str(row.cmt_author_timestamp) + ',' + row.cmt_author_email + ',' + last_github + ',' 
        csv_output.write(basic_info)
 
        top_contribs = all_commits.loc[all_commits['repo_id'] == row.repo_id].cmt_author_email.value_counts()

        # Get github ids for emails
        try:
            most_github = str(id_dict[top_contribs.index[0]][0])
        except:
            most_github = 'None'
        try:
            second_github = str(id_dict[top_contribs.index[1]][0])
        except:
            second_github = 'None'

#        print(last_github, most_github, second_github)

        if len(top_contribs) > 1:
            committer_info = top_contribs.index[0] + ',' + most_github + ',' + str(top_contribs[0]) + ',' + top_contribs.index[1] + ',' + second_github + ',' + str(top_contribs[1]) + '\n'
        elif len(top_contribs) == 1:
            committer_info = top_contribs.index[0] + ',' + most_github + ',' + str(top_contribs[0]) + ',' + 'None' + ',' + 'None' + '\n'
        elif len(top_contribs) == 0:
            committer_info = 'None' + ',' + 'None' + ',' + 'None' + ',' + 'None' + '\n'
        csv_output.write(committer_info)
#        except:
#            csv_output.write(repo_link + ',' + org + ',' + row.repo_name + ',API_ERROR,,,,,,\n')

