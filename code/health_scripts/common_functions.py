def augur_db_connect():
    import psycopg2
    import sqlalchemy as s
    import json
    from os.path import dirname, join
    current_dir = dirname(__file__)
    file_path = join(current_dir, "./config.json")

    with open(file_path) as config_file:
        config = json.load(config_file)

    database_connection_string = 'postgres+psycopg2://{}:{}@{}:{}/{}'.format(config['user'], config['password'], config['host'], config['port'], config['database'])

    dbschema='augur_data'
    engine = s.create_engine(
        database_connection_string,
        connect_args={'options': '-csearch_path={}'.format(dbschema)})

    return engine

def build_id_map(engine):
    # Create a dictionary that maps email addresses to github ids
    import pandas as pd
    import warnings

    # Ignores warning about not unique. This is caused by null values being not unique :shrug:
    warnings.simplefilter("ignore")
    print("Builing map of email addresses to GitHub Ids.")

    id_dict = {}
    id_df = pd.DataFrame()
    id_df_query = f"""
            SELECT cntrb_email, cntrb_login from contributors
            """
    id_df = pd.read_sql_query(id_df_query, con=engine)
    id_dict = id_df.set_index('cntrb_email').T.to_dict('list')
    id_dict

    return id_dict

def get_commits_by_repo(start_date, end_date, engine):
    import pandas as pd

    repo_list_commits = pd.DataFrame()
    repo_list_commits_query = f"""
            SELECT COUNT(DISTINCT commits.cmt_commit_hash), repo.repo_id, repo.repo_name, repo.repo_path from repo, commits
            WHERE 
                repo.repo_id = commits.repo_id
                AND commits.cmt_author_timestamp >= {start_date}
                AND commits.cmt_author_timestamp <= {end_date}
                AND cmt_author_name NOT LIKE '%%utomation%%'
                AND cmt_author_name NOT LIKE '%%ipeline%%'
                AND cmt_author_name NOT LIKE '%%Cloud Foundry%%'
                AND cmt_author_name NOT LIKE 'snyk%%'
                AND cmt_author_name NOT LIKE '%%bot'
                AND cmt_author_name NOT LIKE 'dependabot%%'
                AND cmt_author_name NOT LIKE 'gerrit%%'
                AND cmt_author_name NOT LIKE '%%Bot'
                AND cmt_author_name NOT LIKE '%%BOT'
                AND cmt_author_name != 'cfcr'
                AND cmt_author_name != 'CFCR'
                AND cmt_author_name != 'Travis CI'
                AND cmt_author_name != 'Cloud Foundry London'
                AND cmt_author_name != 'pivotal-rabbitmq-ci'
                AND cmt_author_name != 'Bitnami Containers'
                AND cmt_author_name != 'Spring Operator'
                AND cmt_author_name != 'Spring Buildmaster'
            GROUP BY repo.repo_id
            ORDER BY COUNT(DISTINCT commits.cmt_commit_hash);
            """
    repo_list_commits = pd.read_sql_query(repo_list_commits_query, con=engine)

    return repo_list_commits

def get_overall_risk(sustain_risk, contrib_risk, response_risk, release_risk):
    # calculate overall risk score
    risk_count = [sustain_risk, contrib_risk, response_risk, release_risk].count('AT RISK')
    no_data_count = [sustain_risk, contrib_risk, response_risk].count('NO DATA')
    pr_data_count = [sustain_risk, response_risk].count('TOO FEW PRs')
    if no_data_count > 0 or pr_data_count > 0:
        overall_risk = 'MISSING DATA'
    elif risk_count == 0:
        overall_risk = 'LOW RISK'
    elif (risk_count == 1 or risk_count == 2):
        overall_risk = 'MEDIUM RISK'
    elif (risk_count == 3 or risk_count == 4):
        overall_risk = 'HIGH RISK'

    return overall_risk

def write_overall_risk_file(repo_name, org_name, overall_risk, sustain_risk, contrib_risk, response_risk, release_risk):
    import sys

    path = output_path(repo_name, org_name)
    filename = path + '/' + repo_name + '_overall_risk.txt'

    try:
        output = open(filename, 'w')
        output.write('Overall risk for ' + repo_name + ': ' + overall_risk + '\n\n')
        output.write('Sustains / Keeps up with contributions: ' + sustain_risk + '\n')
        output.write('Contributor risk: ' + contrib_risk + '\n')
        output.write('Timely responses: ' + response_risk + '\n')
        output.write('Releases: ' + release_risk + '\n')
    except:
        print('Could not write overall risk to file. Exiting')
        sys.exit(1)

def get_repo_info(engine):
    import sys
    import pandas as pd

    # read org name and repo name from command line and convert to repo_id
    try:
        repo_org = str(sys.argv[1])
        repo_name = str(sys.argv[2])

    except:
        print("Please enter a case-sensitive org and repo when prompted.")
        print("You must use the case from GitHub; for example, Spring-project must be capitalized.")
        repo_org = input("Enter a GitHub org name: ")
        repo_name = input("Enter a repo name: ")

    try:
        get_id_query = f"""
            SELECT
                repo.repo_id
            FROM
                repo, repo_groups
            WHERE
                repo.repo_group_id = repo_groups.repo_group_id
                AND LOWER(repo.repo_name) = LOWER('{repo_name}')
                AND LOWER(repo_groups.rg_name) = LOWER('{repo_org}');
            """

        repo_id_df = pd.read_sql_query(get_id_query, con=engine)

    except:
        print("Missing or invalid GitHub organization and repository name combination.")
        quit()

    if len(repo_id_df) == 1:
        repo_id = repo_id_df.repo_id[0]
    else:
        print("Missing or invalid GitHub organization and repository name combination.")
        quit()

    return repo_id, repo_org, repo_name

def get_last_month():
    import datetime 

    current = datetime.date.today()

    first_current = current.replace(day=1)
    last_month = first_current - datetime.timedelta(days=1)

    return(last_month)

def get_dates(days):
    import datetime 

    last_month = get_last_month()
    end_date = "'" + str(last_month) + "'"

    start = last_month - datetime.timedelta(days=days)
    start_date = "'" + str(start) + "'"

    return start_date, end_date

def convert_to_dt(start_date, end_date):
    from datetime import datetime, timezone

    # inputs will be date strings, output tz aware datetime

    end_dt = datetime.strptime(end_date, "'%Y-%m-%d'").replace(tzinfo=timezone.utc)

    start_dt = datetime.strptime(start_date, "'%Y-%m-%d'").replace(tzinfo=timezone.utc)

    return start_dt, end_dt

def read_key(file_name):

    from os.path import dirname, join

    # Reads the first line of a file containing the GitHub API key
    # Usage: key = read_key('gh_key')

    current_dir = dirname(__file__)
    file2 = "./" + file_name
    file_path = join(current_dir, file2)

    with open(file_path, 'r') as kf:
        key = kf.readline().rstrip() # remove newline & trailing whitespace
    return key

def fork_archive(repo_name_orig, org_name, engine):
    # Get this data from Augur, instead of GH now that these have been
    # added to the db

    import pandas as pd

    repo_path = "'" + 'github.com/' + org_name + '/' + "'"
    repo_name = "'" + repo_name_orig + "'"

    repo_df = pd.DataFrame()
    repo_df_query = f"""
            SELECT forked_from, repo_archived from repo
            WHERE repo_name = {repo_name}
            AND repo_path = {repo_path}
            """
    repo_df = pd.read_sql_query(repo_df_query, con=engine)
    forked = repo_df.forked_from[0]
    archived = repo_df.repo_archived[0]
    
    is_archived = 'ERROR'
    
    if forked != 'Parent not available':
        is_forked = True
    else:
        is_forked = False
    
    if archived == 1:
       is_archived = True
    elif archived == 0:
       is_archived = False

    return is_forked, is_archived

def repo_api_call(repo_name, org_name):
    from github import Github
    import sys

    try:
        gh_key = read_key('gh_key')
        g = Github(gh_key)

        repo = g.get_repo(org_name + '/' + repo_name)

    except:
        print("Error making GH API call for", org_name, repo_name, "Rate limit remaining", g.rate_limiting[0])
        if g.rate_limiting[0] < 5:
            print("Exiting due to rate limit")
            sys.exit()
        else:
            repo = False

    return repo

def get_release_data(repo_name, org_name, start_date, end_date, repo_api):
    import pandas as pd
    import datetime 

    releases = repo_api.get_releases()

    releases_df = pd.DataFrame(
        [x, x.tag_name, x.published_at] for x in releases
    )
    releases_df.columns = ['release', 'name', 'date']

    return releases_df

def convert_dates(start_date, end_date):
    import datetime

    start_dt = datetime.datetime.strptime(start_date[1:11], '%Y-%m-%d')
    end_dt = datetime.datetime.strptime(end_date[1:11], '%Y-%m-%d')

    return start_dt, end_dt 

def activity_release(repo_name, org_name, start_date, end_date, repo_api):
    import seaborn as sns
    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    import datetime

    try:
        releases_df = get_release_data(repo_name, org_name, start_date, end_date, repo_api)
    except:
        return -1, 'NO DATA'

    start_dt, end_dt = convert_dates(start_date, end_date)
    six_mos_dt = end_dt - datetime.timedelta(days=180)

    risk_num = 0
    for release in releases_df['date']:
        if (release >= six_mos_dt and release <= end_dt):
            risk_num+=1

    # return before creating plots if no release data in past 6 months
    if risk_num == 0:
        return -1, 'NO DATA'

    matplotlib.use('Agg') #prevents from tying to send plot to screen
    sns.set(style="whitegrid", font_scale=2)

    fig, ax = plt.subplots()

    # the size of A4 paper
    fig.set_size_inches(24, 8)

    title = repo_name + "\nActively Maintained - Regular Releases:"

    if risk_num < 5:
        risk = 'AT RISK'
        title += " AT RISK\n" + str(risk_num) + " releases in the past 6 months."
        title_color = 'firebrick'
    else:
        risk = 'HEALTHY'
        title += " Healthy\n" + str(risk_num) + " releases in the past 6 months."
        title_color = 'forestgreen'

    ax.set_xlim(start_dt, end_dt)
    ax.set_ylim(0,2)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.set(yticklabels=[])

    plottermonth = sns.lineplot(y=1, x='date', data=releases_df, marker="X", linewidth=0, markersize=20).set_title(title, fontsize=30, color=title_color)
    plottermonthlabels = ax.set_xlabel('Year Month\n\nInterpretation: Healthy projects will have at least 5 releases in the past 6 months.')

    filename = output_filename(repo_name, org_name, 'activity_release')

    fig.savefig(filename, bbox_inches='tight')
    plt.close(fig)

    print('\nActivity Release metric for', repo_name, '\nfrom', start_date, 'to', end_date, '\nsaved as', filename)
    print(risk, '-', risk_num, 'releases in the past 6 months\n')

    return risk_num, risk

def monthly_prs_closed(repo_id, repo_name, start_date, end_date, engine):
    import pandas as pd

    pr_monthDF = pd.DataFrame()
    pr_monthquery = f"""
                    SELECT
                        * 
                    FROM
                        (
                        SELECT
                            date_part( 'year', month :: DATE ) AS YEAR,
                            date_part( 'month', month :: DATE ) AS month 
                        FROM
                            ( SELECT * FROM ( SELECT month :: DATE FROM generate_series ( TIMESTAMP {start_date}, TIMESTAMP {end_date}, INTERVAL '1 month' ) month ) d ) x 
                        ) y
                        LEFT OUTER JOIN (
                        SELECT
                            repo_id,
                            repo_name,
                            repo_group,
                            date_part( 'year', pr_created_at :: DATE ) AS YEAR,
                            date_part( 'month', pr_created_at :: DATE ) AS month,
                            COUNT ( pr_src_id ) AS total_prs_open_closed 
                        FROM
                            (
                            SELECT
                                repo.repo_id AS repo_id,
                                repo.repo_name AS repo_name,
                                repo_groups.rg_name AS repo_group,
                                pull_requests.pr_created_at AS pr_created_at,
                                pull_requests.pr_closed_at AS pr_closed_at,
                                pull_requests.pr_src_id AS pr_src_id
                            FROM
                                repo,
                                repo_groups,
                                pull_requests 
                            WHERE
                                repo.repo_group_id = repo_groups.repo_group_id 
                                AND repo.repo_id = pull_requests.repo_id 
                                AND repo.repo_id = {repo_id} 
                                AND pull_requests.pr_src_state = 'closed'  
                            ) L 
                        GROUP BY
                            L.repo_id,
                            L.repo_name,
                            L.repo_group,
                            YEAR,
                            month 
                        ORDER BY
                            repo_id,
                            YEAR,
                            month 
                        ) T USING ( month, YEAR ) 
                    ORDER BY
                        YEAR,
                        month;

        """
    pr_monthDFa = pd.read_sql_query(pr_monthquery, con=engine)

    pr_monthDFa[['repo_id']] = pr_monthDFa[['repo_id']].fillna(value=repo_id)
    
    # Hack to fill in repo_name where there are nan's
    pr_monthDFa[['repo_name']] = pr_monthDFa[['repo_name']].fillna(value=repo_name)
    
    pr_monthDF = pr_monthDFa
    pr_monthDF.set_index('repo_id', 'year', 'month')


    pr_monthDF[['total_prs_open_closed']] = pr_monthDF[['total_prs_open_closed']].fillna(0)

    pr_monthDF['year'] = pr_monthDF['year'].map(int)
    pr_monthDF['month'] = pr_monthDF['month'].map(int)
    pr_monthDF['month'] = pr_monthDF['month'].apply('{:0>2}'.format)
    pr_monthDF['yearmonth'] = pr_monthDF['year'].map(str) + '-' + pr_monthDF['month'].map(str)

    return pr_monthDF

def monthly_prs_all(repo_id, repo_name, start_date, end_date, engine):
    import pandas as pd

    pr_monthDF = pd.DataFrame()

    pr_monthquery = f"""
                    SELECT
                        * 
                    FROM
                        (
                        SELECT
                            date_part( 'year', month :: DATE ) AS YEAR,
                            date_part( 'month', month :: DATE ) AS month 
                        FROM
                            ( SELECT * FROM ( SELECT month :: DATE FROM generate_series ( TIMESTAMP {start_date}, TIMESTAMP {end_date}, INTERVAL '1 month' ) month ) d ) x 
                        ) y
                        LEFT OUTER JOIN (
                        SELECT
                            repo_id,
                            repo_name,
                            repo_group,
                            date_part( 'year', pr_created_at :: DATE ) AS YEAR,
                            date_part( 'month', pr_created_at :: DATE ) AS month,
                            COUNT ( pr_src_id ) AS total_prs_open_closed 
                        FROM
                            (
                            SELECT
                                repo.repo_id AS repo_id,
                                repo.repo_name AS repo_name,
                                repo_groups.rg_name AS repo_group,
                                pull_requests.pr_created_at AS pr_created_at,
                                pull_requests.pr_closed_at AS pr_closed_at,
                                pull_requests.pr_src_id AS pr_src_id
                            FROM
                                repo,
                                repo_groups,
                                pull_requests 
                            WHERE
                                repo.repo_group_id = repo_groups.repo_group_id 
                                AND repo.repo_id = pull_requests.repo_id 
                                AND repo.repo_id = {repo_id} 
                            ) L 
                        GROUP BY
                            L.repo_id,
                            L.repo_name,
                            L.repo_group,
                            YEAR,
                            month 
                        ORDER BY
                            repo_id,
                            YEAR,
                            month 
                        ) T USING ( month, YEAR ) 
                    ORDER BY
                        YEAR,
                        month;

        """
    pr_monthDFa = pd.read_sql_query(pr_monthquery, con=engine)

    pr_monthDFa[['repo_id']] = pr_monthDFa[['repo_id']].fillna(value=repo_id)
    
    # Hack to fill in repo_name where there are nan's
    pr_monthDFa[['repo_name']] = pr_monthDFa[['repo_name']].fillna(value=repo_name)
    
    pr_monthDF = pr_monthDFa
    pr_monthDF.set_index('repo_id', 'year', 'month')

    pr_monthDF[['total_prs_open_closed']] = pr_monthDF[['total_prs_open_closed']].fillna(0)

    return pr_monthDF

def commit_author_data(repo_id, repo_name, start_date, end_date, engine):

    import pandas as pd

    start_date, end_date = convert_to_dt(start_date, end_date)

    #Commit data - from humans excluding known bots
    commitsDF = pd.DataFrame()
    commitsquery = f"""
                    SELECT
                        DISTINCT(cmt_commit_hash),
                        contributors.cntrb_canonical,
                        canonical_full_names.cntrb_full_name AS canonical_full_name,
                        cmt_author_name, cmt_author_email, repo_id, cmt_author_timestamp 
                    FROM commits 
                        LEFT OUTER JOIN contributors ON cntrb_email = cmt_author_email left outer join 
                        (
                            SELECT distinct on (cntrb_canonical) cntrb_full_name, cntrb_canonical, data_collection_date
                            FROM contributors
                            WHERE cntrb_canonical = cntrb_email
                            order by cntrb_canonical
                        ) canonical_full_names on canonical_full_names.cntrb_canonical = contributors.cntrb_canonical
                    WHERE 
                        repo_id = {repo_id}
                        AND cmt_author_name NOT LIKE 'snyk%%'
                        AND cmt_author_name NOT LIKE '%%bot'
                        AND cmt_author_name NOT LIKE '%%Bot'
                        AND cmt_author_name NOT LIKE '%%BOT'
                        AND cmt_author_name NOT LIKE 'dependabot%%'
                        AND cmt_author_name NOT LIKE 'gerrit%%'
                        AND cmt_author_name NOT LIKE '%%utomation%%'
                        AND cmt_author_name NOT LIKE '%%ipeline%%'
                        AND cmt_author_name NOT LIKE '%%Cloud Foundry%%'
                        AND cmt_author_name != 'cfcr'
                        AND cmt_author_name != 'CFCR'
                        AND cmt_author_name != 'Travis CI'
                        AND cmt_author_name != 'Bitnami Containers'
                        AND cmt_author_name != 'Cloud Foundry London'
                        AND cmt_author_name != 'Spring Operator'
                        AND cmt_author_name != 'Spring Buildmaster'
                        AND cmt_author_name != 'pivotal-rabbitmq-ci'
                    ORDER BY
                        cntrb_canonical;
                    """
    
    all_commitsDF = pd.read_sql_query(commitsquery, con=engine)
    commitsDF = all_commitsDF[(all_commitsDF['cmt_author_timestamp'] >= start_date) & (all_commitsDF['cmt_author_timestamp'] <= end_date)]
    total_commits = commitsDF.cmt_commit_hash.nunique()    

    authorDF = pd.DataFrame()
    authorDF = commitsDF.canonical_full_name.value_counts()
    authorDF = authorDF.reset_index()
    authorDF.columns = ['name', 'commits']
    authorDF['percent'] = authorDF['commits'] / total_commits

    return authorDF

def output_path(repo_name, org_name):
    import datetime
    from os.path import dirname, join
    from pathlib import Path

    today = datetime.date.today()
    last_month = get_last_month()
    current_year_month = str(last_month.year) + '-' + '{:02d}'.format(last_month.month)
    #current_year_month = str(today.year) + '-' + '{:02d}'.format(last_month.month)

    current_dir = dirname(__file__)
    rel_path = './output/' + current_year_month + '/' + org_name + '/' + repo_name 
    path = join(current_dir, rel_path)
    Path(path).mkdir(parents=True, exist_ok=True)

    return path

def output_filename(repo_name, org_name, metric_string): 

    path = output_path(repo_name, org_name)

    filename = path + '/' + repo_name + '_' + metric_string + '.png'

    return filename

def contributor_risk(repo_id, repo_name, org_name, start_date, end_date, engine):

    import pandas as pd
    import seaborn as sns
    import matplotlib
    import matplotlib.pyplot as plt
    import textwrap

    authorDF = commit_author_data(repo_id, repo_name, start_date, end_date, engine)

    cum_percent = 0
    people_list = []

    i = 1
    num_people = 0

    for item in authorDF.iterrows():
        name = item[1]['name']
        percent = item[1]['percent']
        commits = item[1]['commits']
    
        cum_percent += percent
    
        people_list.append([name, percent, commits])
    
        if (cum_percent > .70 and num_people == 0):
            num_people = i
            risk_percent = cum_percent
        
        if i == 8:
            if cum_percent <= .70:
                risk_percent = cum_percent
                num_people = i
            break
        i+=1
    
    risk_list = []
    bar_colors = []

    j = 1
    for person in people_list:
        name = person[0]
        if len(name) > 15:
            new_name = textwrap.wrap(name, 15)
            name = '\n'.join(new_name)
        percent = person[1]
        commits = person[2]
        risk_list.append([name, percent, commits])
    
        if (num_people < 3 and j <= num_people):
            bar_colors.append('red')
        else:
            bar_colors.append('lightblue')
    
        j+=1

    # Exit early if num_people is 0
    if num_people == 0:
        return -1, 'NO DATA'
    
    names = [item[0] for item in risk_list]
    percents = [item[1] for item in risk_list]
    commits = [item[2] for item in risk_list]

    matplotlib.use('Agg') #prevents from tying to send plot to screen
    sns.set_style('ticks')
    sns.set(style="whitegrid", font_scale=2)

    fig, ax = plt.subplots()

    # the size of A4 paper
    fig.set_size_inches(24, 8)

    title = repo_name + "\nContributor Risk: "

    if num_people < 3:
        risk = 'AT RISK'
        title += "AT RISK"
        title_color = 'firebrick'
    else:
        risk = 'HEALTHY'
        title += "Healthy"
        title_color = 'forestgreen'

    # reformat dates
    start = start_date.replace("'", '')
    end = end_date.replace("'", '')
    title += "\n" + str(num_people) + " people made up " + "{:.0%}".format(risk_percent) + " of the commits from " + start + " to " + end + ".\n"

    risk_bar = sns.barplot(x=names, y=commits, palette=bar_colors).set_title(title, fontsize=30, color=title_color)

    risk_bar_labels = ax.set_xticklabels(names, wrap=True)
    risk_bar_labels = ax.set_ylabel('Commits')
    risk_bar_labels = ax.set_xlabel('\nKey Contributors\n\nInterpretation: Healthy projects should have at minimum 3 people who combined account for the majority (>70%) of the commits.\nThe higher this number is, the more likely your project would succeed if a leading contributor suddenly left the project.\nRed bars indicate when less than 3 people have 70% of commits. Light blue for other contributors.')

    i = 0
    for p in ax.patches:
        ax.annotate("{:.0%}".format(percents[i]), (p.get_x() + p.get_width() / 2., p.get_height()),
            ha='center', va='center', color='gray', xytext=(0, 20),
            textcoords='offset points')
        i+=1

    filename = output_filename(repo_name, org_name, 'contrib_risk_commits')

    fig.savefig(filename, bbox_inches='tight')
    plt.close(fig)

    print('\nContributor Risk for', repo_name, '\nfrom', start_date, 'to', end_date, '\nsaved as', filename)
    print(risk, '-', num_people, 'people make up > 70% of the commits in the past year\n')

    return num_people, risk

def response_time_db(repo_id, repo_name, start_date, end_date, engine):

    import pandas as pd
    import sqlalchemy as s

    pr_all = pd.DataFrame()

    pr_query = s.sql.text(f"""
                    SELECT
                        repo.repo_id AS repo_id,
                        pull_requests.pr_src_id AS pr_src_id,
                        repo.repo_name AS repo_name,
                        pr_src_author_association,
                        repo_groups.rg_name AS repo_group,
                        pull_requests.pr_src_state,
                        pull_requests.pr_merged_at,
                        pull_requests.pr_created_at AS pr_created_at,
                        pull_requests.pr_closed_at AS pr_closed_at,
                        date_part( 'year', pr_created_at :: DATE ) AS CREATED_YEAR,
                        date_part( 'month', pr_created_at :: DATE ) AS CREATED_MONTH,
                        date_part( 'year', pr_closed_at :: DATE ) AS CLOSED_YEAR,
                        date_part( 'month', pr_closed_at :: DATE ) AS CLOSED_MONTH,
                        pr_src_meta_label,
                        pr_head_or_base,
                        ( EXTRACT ( EPOCH FROM pull_requests.pr_closed_at ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 3600 AS hours_to_close,
                        ( EXTRACT ( EPOCH FROM pull_requests.pr_closed_at ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 86400 AS days_to_close, 
                        ( EXTRACT ( EPOCH FROM first_response_time ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 3600 AS hours_to_first_response,
                        ( EXTRACT ( EPOCH FROM first_response_time ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 86400 AS days_to_first_response, 
                        ( EXTRACT ( EPOCH FROM last_response_time ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 3600 AS hours_to_last_response,
                        ( EXTRACT ( EPOCH FROM last_response_time ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 86400 AS days_to_last_response, 
                        first_response_time,
                        last_response_time,
                        average_time_between_responses,
                        assigned_count,
                        review_requested_count,
                        labeled_count,
                        subscribed_count,
                        mentioned_count,
                        referenced_count,
                        closed_count,
                        head_ref_force_pushed_count,
                        merged_count,
                        milestoned_count,
                        unlabeled_count,
                        head_ref_deleted_count,
                        comment_count,
                        lines_added, 
                        lines_removed,
                        commit_count, 
                        file_count
                    FROM
                    repo,
                    repo_groups,
                    pull_requests LEFT OUTER JOIN ( 
                            SELECT pull_requests.pull_request_id,
                                MIN(message.msg_timestamp) AS first_response_time,
                                COUNT(DISTINCT message.msg_timestamp) AS comment_count,
                                MAX(message.msg_timestamp) AS last_response_time,
                                (MAX(message.msg_timestamp) - MIN(message.msg_timestamp)) / COUNT(DISTINCT message.msg_timestamp) AS average_time_between_responses
                            FROM repo, 
                                pull_requests left outer join pull_request_message_ref 
                                on pull_requests.pull_request_id = pull_request_message_ref.pull_request_id
                                left outer join message on pull_request_message_ref.msg_id = message.msg_id and cntrb_id not in (select cntrb_id from contributors where cntrb_login like '%[bot]')
                            WHERE repo.repo_id = {repo_id}
                            AND repo.repo_id = pull_requests.repo_id
                            GROUP BY pull_requests.pull_request_id
                    ) response_times
                    ON pull_requests.pull_request_id = response_times.pull_request_id
                    left outer join (
                            SELECT pull_requests.pull_request_id,
                                count(*) FILTER (WHERE action = 'assigned') AS assigned_count,
                                count(*) FILTER (WHERE action = 'review_requested') AS review_requested_count,
                                count(*) FILTER (WHERE action = 'labeled') AS labeled_count,
                                count(*) FILTER (WHERE action = 'unlabeled') AS unlabeled_count,
                                count(*) FILTER (WHERE action = 'subscribed') AS subscribed_count,
                                count(*) FILTER (WHERE action = 'mentioned') AS mentioned_count,
                                count(*) FILTER (WHERE action = 'referenced') AS referenced_count,
                                count(*) FILTER (WHERE action = 'closed') AS closed_count,
                                count(*) FILTER (WHERE action = 'head_ref_force_pushed') AS head_ref_force_pushed_count,
                                count(*) FILTER (WHERE action = 'head_ref_deleted') AS head_ref_deleted_count,
                                count(*) FILTER (WHERE action = 'milestoned') AS milestoned_count,
                                count(*) FILTER (WHERE action = 'merged') AS merged_count
                            from repo, pull_requests left outer join pull_request_events 
                                on pull_requests.pull_request_id = pull_request_events.pull_request_id
                            WHERE repo.repo_id = {repo_id}
                                AND repo.repo_id = pull_requests.repo_id
                            GROUP BY pull_requests.pull_request_id
                    ) event_counts on event_counts.pull_request_id = pull_requests.pull_request_id
                    LEFT OUTER JOIN (
                            SELECT pull_request_commits.pull_request_id, count(DISTINCT pr_cmt_sha) AS commit_count                                FROM pull_request_commits, pull_requests, pull_request_meta
                            WHERE pull_requests.pull_request_id = pull_request_commits.pull_request_id
                            AND pull_requests.pull_request_id = pull_request_meta.pull_request_id
                            AND pull_requests.repo_id = {repo_id}
                            AND pr_cmt_sha <> pull_requests.pr_merge_commit_sha
                            AND pr_cmt_sha <> pull_request_meta.pr_sha
                            GROUP BY pull_request_commits.pull_request_id
                    ) all_commit_counts
                    ON pull_requests.pull_request_id = all_commit_counts.pull_request_id
                    LEFT OUTER JOIN (
                            SELECT MAX(pr_repo_meta_id), pull_request_meta.pull_request_id, pr_head_or_base, pr_src_meta_label
                            FROM pull_requests, pull_request_meta
                            WHERE pull_requests.pull_request_id = pull_request_meta.pull_request_id
                            AND pull_requests.repo_id = {repo_id}
                            AND pr_head_or_base = 'base'
                            GROUP BY pull_request_meta.pull_request_id, pr_head_or_base, pr_src_meta_label
                    ) base_labels
                    ON base_labels.pull_request_id = pull_requests.pull_request_id
                    LEFT OUTER JOIN (
                            SELECT sum(cmt_added) AS lines_added, sum(cmt_removed) AS lines_removed, pull_request_commits.pull_request_id, count(DISTINCT cmt_filename) AS file_count
                            FROM pull_request_commits, commits, pull_requests, pull_request_meta
                            WHERE cmt_commit_hash = pr_cmt_sha
                            AND pull_requests.pull_request_id = pull_request_commits.pull_request_id
                            AND pull_requests.pull_request_id = pull_request_meta.pull_request_id
                            AND pull_requests.repo_id = {repo_id}
                            AND commits.repo_id = pull_requests.repo_id
                            AND commits.cmt_commit_hash <> pull_requests.pr_merge_commit_sha
                            AND commits.cmt_commit_hash <> pull_request_meta.pr_sha
                            GROUP BY pull_request_commits.pull_request_id
                    ) master_merged_counts 
                    ON pull_requests.pull_request_id = master_merged_counts.pull_request_id                   
                    WHERE 
                        repo.repo_group_id = repo_groups.repo_group_id 
                        AND repo.repo_id = pull_requests.repo_id 
                        AND repo.repo_id = {repo_id}
                        AND pr_created_at >= {start_date}
                        AND pr_created_at <= {end_date}
                    ORDER BY
                       merged_count DESC
                    """)
    pr_a = pd.read_sql(pr_query, con=engine)
    pr_all = pr_a

    return pr_all

def response_time_data(repo_id, repo_name, org_name, start_date, end_date, engine):
    import pandas as pd
    import numpy as np
    import datetime
    from dateutil.relativedelta import relativedelta
    from pandas.tseries.offsets import BusinessDay

    pr_all = response_time_db(repo_id, repo_name, start_date, end_date, engine)

    bd = pd.tseries.offsets.BusinessDay(n = 2)

    # Don't gather data if less than 24 PRs
    if len(pr_all) < 24:
        return -1, 'TOO FEW PRs', pr_all, '', '', '', -1, -1
    else:
        error_num = 0
        error_text = 'NA'

    # Exit if diff can't be calculate (usu no responses)
    try:
        pr_all['diff'] = pr_all.first_response_time - pr_all.pr_created_at
        pr_all['2_bus_days'] = pr_all.pr_created_at + bd
        pr_all['yearmonth'] = pr_all['pr_created_at'].dt.strftime('%Y-%m')
        pr_all['in_guidelines'] = np.where(pr_all['2_bus_days'] < pr_all['first_response_time'], 0, 1)
        error_num = 0
        error_text = 'NA'

    except:
        return -1, 'NO DATA', pr_all, '', '', '', -1, -1

    year_month_list = pr_all.yearmonth.unique()
    year_month_list.sort()
    first_response = pr_all.groupby(['repo_name', 'yearmonth'], as_index=False).sum()[['repo_name', 'yearmonth', 'in_guidelines']]

    # counts total number of PRs each month
    total_by_month = pr_all.groupby(['repo_name', 'yearmonth'], as_index=False).count()[['repo_name', 'yearmonth', 'pr_created_at']]

    first_response['total_prs'] = total_by_month['pr_created_at']
    first_response['out_guidelines'] = first_response['total_prs'] - first_response['in_guidelines']
    first_response['in_percent'] = first_response['in_guidelines'] / first_response['total_prs']
    first_response['out_percent'] = first_response['out_guidelines'] / first_response['total_prs']

    risk_num = 0
    six_months = str(datetime.date.today() + relativedelta(months=-7)) # 7 because we don't gather current partial month data
    for item in first_response.iterrows():
        year_month = item[1]['yearmonth']
        percent = item[1]['out_percent']
        if (percent > 0.10 and year_month >= six_months):
            risk_num+=1

    title = repo_name + "\nTimely Responses:"

    if risk_num >= 2:
        risk = 'AT RISK'
        title += " AT RISK\n" + str(risk_num) + " month(s) with > 10% of pull requests not responded to within 2 business days in the past 6 months."
        title_color = 'firebrick'
    else:
        risk = 'HEALTHY'
        title += " Healthy\nMore than 90% of pull requests responded to within 2 business days for " + str(6 - risk_num) + " out of the past 6 months."
        title_color = 'forestgreen'

    interpretation = 'Interpretation: Healthy projects will have little or no gap. A large or increasing gap requires attention.'
    
    return error_num, error_text, first_response, title, title_color, interpretation, risk, risk_num

def response_time_graph(repo_id, repo_name, org_name, start_date, end_date, engine):
    import pandas as pd
    import numpy as np
    import seaborn as sns
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    import warnings
    
    warnings.simplefilter("ignore") # Ignore fixed formatter warning.

    error_num, error_text, first_response, title, title_color, interpretation, risk, risk_num = response_time_data(repo_id, repo_name, org_name, start_date, end_date, engine)

    # Don't gather data if less than 24 PRs
    if error_num == -1:
        return -1, 'TOO FEW PRs'

    sns.set_style('ticks')
    sns.set(style="whitegrid", font_scale=2)

    fig, ax = plt.subplots()
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    # the size of A4 paper
    fig.set_size_inches(24, 8)

    plottermonth = sns.lineplot(x='yearmonth', y='total_prs', data=first_response, sort=False, color='black', label='Total', linewidth=2.5)
    plottermonth = sns.lineplot(x='yearmonth', y='in_guidelines', data=first_response, sort=False, color='green', label='Response < 2 bus days', linewidth=2.5, linestyle='dashed').set_title(title, fontsize=30, color=title_color) 

    plottermonthlabels = ax.set_xticklabels(first_response['yearmonth'])
    plottermonthlabels = ax.set_ylabel('Number of PRs')
    interpretation_str = 'Year Month\n\n' + interpretation
    plottermonthlabels = ax.set_xlabel(interpretation_str)

    filename = output_filename(repo_name, org_name, 'first_response_pr')

    fig.savefig(filename, bbox_inches='tight')
    plt.close(fig)

    print('\nTime to first response for', repo_name, '\nfrom', start_date, 'to', end_date, '\nsaved as', filename)
    print(risk, '-', risk_num, 'months with more than 10% of pull requests not responded to within 2 business days in the past 6 months\n')

    return risk_num, risk

def response_time(repo_id, repo_name, org_name, start_date, end_date, engine):
    import pandas as pd
    import numpy as np
    import seaborn as sns
    import matplotlib
    import matplotlib.pyplot as plt
    import datetime
    from dateutil.relativedelta import relativedelta
    from pandas.tseries.offsets import BusinessDay
    from matplotlib.ticker import MaxNLocator

    pr_all = response_time_db(repo_id, repo_name, start_date, end_date, engine)

    bd = pd.tseries.offsets.BusinessDay(n = 2) 

    # Don't gather data if less than 24 PRs
    if len(pr_all) < 24:
        return -1, 'TOO FEW PRs'

    # Exit if diff can't be calculate (usu no responses)
    try:
        pr_all['diff'] = pr_all.first_response_time - pr_all.pr_created_at
        pr_all['2_bus_days'] = pr_all.pr_created_at + bd
        pr_all['yearmonth'] = pr_all['pr_created_at'].dt.strftime('%Y-%m')
        pr_all['in_guidelines'] = np.where(pr_all['2_bus_days'] < pr_all['first_response_time'], 0, 1)

    except:
        return -1, 'NO DATA'

    year_month_list = pr_all.yearmonth.unique()
    year_month_list.sort()
    first_response = pr_all.groupby(['repo_name', 'yearmonth'], as_index=False).sum()[['repo_name', 'yearmonth', 'in_guidelines']]

    # counts total number of PRs each month
    total_by_month = pr_all.groupby(['repo_name', 'yearmonth'], as_index=False).count()[['repo_name', 'yearmonth', 'pr_created_at']]

    first_response['total_prs'] = total_by_month['pr_created_at']
    first_response['out_guidelines'] = first_response['total_prs'] - first_response['in_guidelines']
    first_response['in_percent'] = first_response['in_guidelines'] / first_response['total_prs']
    first_response['out_percent'] = first_response['out_guidelines'] / first_response['total_prs']

    sns.set_style('ticks')
    sns.set(style="whitegrid", font_scale=2)

    fig, ax = plt.subplots()
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    # the size of A4 paper
    fig.set_size_inches(24, 8)

    risk_num = 0
    six_months = str(datetime.date.today() + relativedelta(months=-7)) # 7 because we don't gather current partial month data
    for item in first_response.iterrows():
        year_month = item[1]['yearmonth']
        percent = item[1]['out_percent']
        if (percent > 0.10 and year_month >= six_months):
            risk_num+=1

    title = repo_name + "\nTimely Responses:"

    if risk_num >= 2:
        risk = 'AT RISK'
        title += " AT RISK\n" + str(risk_num) + " month(s) with > 10% of pull requests not responded to within 2 business days in the past 6 months."
        title_color = 'firebrick'
    else:
        risk = 'HEALTHY'
        title += " Healthy\nMore than 90% of pull requests responded to within 2 business days for " + str(6 - risk_num) + " out of the past 6 months."
        title_color = 'forestgreen'

    plottermonth = sns.lineplot(x='yearmonth', y='total_prs', data=first_response, sort=False, color='black', label='Total', linewidth=2.5)
    plottermonth = sns.lineplot(x='yearmonth', y='in_guidelines', data=first_response, sort=False, color='green', label='Response < 2 bus days', linewidth=2.5, linestyle='dashed').set_title(title, fontsize=30, color=title_color) 

    plottermonthlabels = ax.set_xticklabels(first_response['yearmonth'])
    plottermonthlabels = ax.set_ylabel('Number of PRs')
    plottermonthlabels = ax.set_xlabel('Year Month\n\nInterpretation: Healthy projects will have little or no gap. A large or increasing gap requires attention.')

    filename = output_filename(repo_name, org_name, 'first_response_pr')

    fig.savefig(filename, bbox_inches='tight')
    plt.close(fig)

    print('\nTime to first response for', repo_name, '\nfrom', start_date, 'to', end_date, '\nsaved as', filename)
    print(risk, '-', risk_num, 'months with more than 10% of pull requests not responded to within 2 business days in the past 6 months\n')

    return risk_num, risk

def sustain_prs_by_repo_data(repo_id, repo_name, org_name, start_date, end_date, engine):

    import pandas as pd

    all_prsDF = monthly_prs_all(repo_id, repo_name, start_date, end_date, engine)

    # Return with no data if there are no PRs
    if all_prsDF['total_prs_open_closed'].sum() < 24:
        return -1, 'TOO FEW PRs', all_prsDF, '', '', '', -1, -1
    else:
        error_num = 0
        error_text = 'NA'

    closed_prsDF = monthly_prs_closed(repo_id, repo_name, start_date, end_date, engine)

    pr_sustainDF = pd.DataFrame()

    pr_sustainDF['yearmonth'] = closed_prsDF['yearmonth']
    pr_sustainDF['repo_name'] = closed_prsDF['repo_name']
    pr_sustainDF['repo_id'] = closed_prsDF['repo_id']
    pr_sustainDF['closed_total'] = closed_prsDF['total_prs_open_closed']

    pr_sustainDF['all_total'] = all_prsDF['total_prs_open_closed']
    pr_sustainDF['diff'] = pr_sustainDF['all_total'] - pr_sustainDF['closed_total']
    pr_sustainDF['diff_per'] = pr_sustainDF['diff'] / pr_sustainDF['all_total']

    pr_sustainDF['repo_id'] = pr_sustainDF['repo_id'].map(int)
    pr_sustainDF.set_index('repo_id', 'yearmonth')

    risk_num = 0
    m = 1
    for diff_per in pr_sustainDF['diff_per']:
        if (diff_per > 0.10 and m > 6):
            risk_num+=1
        m+=1

    title = pr_sustainDF['repo_name'][0] + "\nSustains and Keeps up with Contributions:"

    if risk_num >= 2:
        risk = 'AT RISK'
        title += " AT RISK\n" + str(risk_num) + " month(s) with > 10% of total pull requests not closed in the past 6 months"
        title_color = 'firebrick'
    else:
        risk = 'HEALTHY'
        title += " Healthy\nMore than 90% of total pull requests were closed for " + str(6 - risk_num) + " out of the past 6 months."
        title_color = 'forestgreen'

    interpretation = 'Interpretation: Healthy projects will have little or no gap. A large or increasing gap requires attention.'

    return error_num, error_text, pr_sustainDF, title, title_color, interpretation, risk, risk_num  

def sustain_prs_by_repo_graph(repo_id, repo_name, org_name, start_date, end_date, engine):

    import pandas as pd
    import seaborn as sns
    import matplotlib
    import matplotlib.pyplot as plt
    import datetime
    from matplotlib.ticker import MaxNLocator
    import warnings

    warnings.simplefilter("ignore") # Ignore fixed formatter warning.

    error_num, error_text, pr_sustainDF, title, title_color, interpretation, risk, risk_num = sustain_prs_by_repo_data(repo_id, repo_name, org_name, start_date, end_date, engine)

    if error_num == -1:
        return -1, 'TOO FEW PRs'

    matplotlib.use('Agg') #prevents from tying to send plot to screen
    sns.set_style('ticks')
    sns.set(style="whitegrid", font_scale=2)

    fig, ax = plt.subplots()
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    # the size of A4 paper
    fig.set_size_inches(24, 8)

    plottermonth = sns.lineplot(x='yearmonth', y='all_total', data=pr_sustainDF, sort=False, color='black', label='Total', linewidth=2.5)
    plottermonth = sns.lineplot(x='yearmonth', y='closed_total', data=pr_sustainDF, sort=False, color='green', label='Closed', linewidth=2.5, linestyle='dashed').set_title(title, fontsize=30, color=title_color)

    plottermonthlabels = ax.set_xticklabels(pr_sustainDF['yearmonth'])
    plottermonthlabels = ax.set_ylabel('Number of PRs')
    xlabel_str = 'Year Month\n\n' + interpretation
    plottermonthlabels = ax.set_xlabel(xlabel_str)

    filename = output_filename(repo_name, org_name, 'sustains_pr')

    fig.savefig(filename, bbox_inches='tight')
    plt.close(fig)

    print('\nSustaining and keeping up with contributions for', repo_name, '\nfrom', start_date, 'to', end_date, '\nsaved as', filename)
    print(risk, '- Number of months in the past 6 months with > 10% of PRs not closed', risk_num, '\n')

    return risk_num, risk

def sustain_prs_by_repo_OBSOLETE(repo_id, repo_name, org_name, start_date, end_date, engine):

    # This function is obsolete and has been replaced by sustain_prs_by_repo_data and sustain_prs_by_repo_graph
    # Keeping this code around until I fully validated my changes

    import pandas as pd
    import seaborn as sns
    import matplotlib
    import matplotlib.pyplot as plt
    import datetime
    from matplotlib.ticker import MaxNLocator
    import warnings
    
    warnings.simplefilter("ignore") # Ignore fixed formatter warning.

    all_prsDF = monthly_prs_all(repo_id, repo_name, start_date, end_date, engine)

    # Return with no data if there are no PRs
    if all_prsDF['total_prs_open_closed'].sum() < 24:
        return -1, 'TOO FEW PRs'

    closed_prsDF = monthly_prs_closed(repo_id, repo_name, start_date, end_date, engine)

    pr_sustainDF = pd.DataFrame()

    pr_sustainDF['yearmonth'] = closed_prsDF['yearmonth']
    pr_sustainDF['repo_name'] = closed_prsDF['repo_name']
    pr_sustainDF['repo_id'] = closed_prsDF['repo_id']
    pr_sustainDF['closed_total'] = closed_prsDF['total_prs_open_closed']

    pr_sustainDF['all_total'] = all_prsDF['total_prs_open_closed']
    pr_sustainDF['diff'] = pr_sustainDF['all_total'] - pr_sustainDF['closed_total']
    pr_sustainDF['diff_per'] = pr_sustainDF['diff'] / pr_sustainDF['all_total']

    # Disply results on a graph
    pr_sustainDF['repo_id'] = pr_sustainDF['repo_id'].map(int)
    pr_sustainDF.set_index('repo_id', 'yearmonth')

    matplotlib.use('Agg') #prevents from tying to send plot to screen
    sns.set_style('ticks')
    sns.set(style="whitegrid", font_scale=2)

    fig, ax = plt.subplots()
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    # the size of A4 paper
    fig.set_size_inches(24, 8)

    risk_num = 0
    m = 1
    for diff_per in pr_sustainDF['diff_per']:
        if (diff_per > 0.10 and m > 6):
            risk_num+=1
        m+=1

    title = pr_sustainDF['repo_name'][0] + "\nSustains and Keeps up with Contributions:"

    if risk_num >= 2:
        risk = 'AT RISK'
        title += " AT RISK\n" + str(risk_num) + " month(s) with > 10% of total pull requests not closed in the past 6 months"
        title_color = 'firebrick'
    else:
        risk = 'HEALTHY'
        title += " Healthy\nMore than 90% of total pull requests were closed for " + str(6 - risk_num) + " out of the past 6 months."
        title_color = 'forestgreen'

    plottermonth = sns.lineplot(x='yearmonth', y='all_total', data=pr_sustainDF, sort=False, color='black', label='Total', linewidth=2.5)
    plottermonth = sns.lineplot(x='yearmonth', y='closed_total', data=pr_sustainDF, sort=False, color='green', label='Closed', linewidth=2.5, linestyle='dashed').set_title(title, fontsize=30, color=title_color) 

    plottermonthlabels = ax.set_xticklabels(pr_sustainDF['yearmonth'])
    plottermonthlabels = ax.set_ylabel('Number of PRs')
    plottermonthlabels = ax.set_xlabel('Year Month\n\nInterpretation: Healthy projects will have little or no gap. A large or increasing gap requires attention.')

    filename = output_filename(repo_name, org_name, 'sustains_pr')

    fig.savefig(filename, bbox_inches='tight')
    plt.close(fig)

    print('\nSustaining and keeping up with contributions for', repo_name, '\nfrom', start_date, 'to', end_date, '\nsaved as', filename)
    print(risk, '- Number of months in the past 6 months with > 10% of PRs not closed', risk_num, '\n')

    return risk_num, risk
