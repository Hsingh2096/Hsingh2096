from github import Github
import pandas as pd 
import sys
from common_functions import read_key

try:
    gh_key = read_key('gh_key_stefka')
    g = Github(gh_key)

except:
    print("Error making GH API call. Rate limit remaining", g.rate_limiting[0])

# prepare csv file and write header row
try:
    csv_output = open('output/a_private_repos.csv', 'w')
    csv_output.write('Repo URL,Last Updated\n')
except:
    print('Could not write to csv file. Exiting')
    sys.exit(1)

org_list = ["pivotal-cf-experimental", "pivotal-cloudops", "pcfdev-forks", "cfmobile", "vmware", "vmware-labs", "vmware-samples", "vmware-tanzu", "vmware-tanzu-private", "pivotal-cf"]

for org in org_list:
    repo_list = g.get_organization(org).get_repos()

    count = 0

    for x in repo_list:
        if x.private == True:
            csv_line = x.html_url + ',' + str(x.updated_at) +  '\n'
            csv_output.write(csv_line)
            count += 1

    print(org, 'has', count, 'private repos')

