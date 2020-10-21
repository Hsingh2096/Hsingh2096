# Usage:
# gh_key is the filename containing your GitHub key
# this file should be in the same directory as the script

from github import Github
import pandas as pd 
import sys
from os.path import dirname, join
from common_functions import read_key

try:
    gh_key = read_key('gh_key')
    g = Github(gh_key)
except:
    print("Error reading GitHub API key. Exiting")
    sys.exit(1)

# prepare csv file and write header row
try:
    current_dir = dirname(__file__)
    file_path = join(current_dir, 'output/a_private_repos.csv')

    csv_output = open(file_path, 'w')
    csv_output.write('Repo URL,Last Updated\n')
except:
    print('Could not write to csv file. Exiting')
    sys.exit(1)

org_list = ["pivotal-cf-experimental", "pivotal-cloudops", "pcfdev-forks", "cfmobile", "vmware", "vmware-labs", "vmware-samples", "vmware-tanzu", "vmware-tanzu-private", "pivotal-cf", "vmwarepivotallabs", "pivotal-gss", "pivotal-data-engineering", "pivotal-DataFabric", "pivotalsoftware", "Pivotal-Field-Engineering", "gemxd", "pivotal"]

print("\nIf any of these counts are 0, the GitHub key might not have access to private repos for that org.")

for org in org_list:

    try:
        repo_list = g.get_organization(org).get_repos()

        count = 0

        for x in repo_list:
            if x.private == True:
                csv_line = x.html_url + ',' + str(x.updated_at) +  '\n'
                csv_output.write(csv_line)
                count += 1

        print(org, 'has', count, 'private repos')

    except:
        print(org, "ERROR: you might have mistyped the name or hit the GH rate limit. Limit remaining:", g.rate_limiting[0])

print("Writing to CSV Complete. Exiting.")
