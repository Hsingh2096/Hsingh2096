def augur_db_connect():
    import psycopg2
    import sqlalchemy as s
    import json

    with open("config.json") as config_file:
        config = json.load(config_file)

    database_connection_string = 'postgres+psycopg2://{}:{}@{}:{}/{}'.format(config['user'], config['password'], config['host'], config['port'], config['database'])

    dbschema='augur_data'
    engine = s.create_engine(
        database_connection_string,
        connect_args={'options': '-csearch_path={}'.format(dbschema)})

    return engine

def get_overall_risk(sustain_risk, contrib_risk, response_risk):
    # calculate overall risk score
    risk_count = [sustain_risk, contrib_risk, response_risk].count('AT RISK')
    no_data_count = [sustain_risk, contrib_risk, response_risk].count('NO DATA')
    if no_data_count > 0:
        overall_risk = 'MISSING DATA'
    elif risk_count == 0:
        overall_risk = 'LOW RISK'
    elif (risk_count == 1 or risk_count == 2):
        overall_risk = 'MEDIUM RISK'
    elif risk_count == 3:
        overall_risk = 'HIGH RISK'

    return overall_risk

def get_repo_info(engine):
    import sys
    import pandas as pd

    # read org name and repo name from command line and convert to repo_id
    try:
        repo_org = str(sys.argv[1])
        repo_name = str(sys.argv[2])

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

def get_dates(days):
    import datetime 

    current = datetime.date.today()

    first_current = current.replace(day=1)
    last_month = first_current - datetime.timedelta(days=1)
    end_date = "'" + str(last_month) + "'"

    start = last_month - datetime.timedelta(days=days)
    start_date = "'" + str(start) + "'"

    return start_date, end_date

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

    #Commit data - from humans excluding known bots
    commitsDF = pd.DataFrame()
    commitsquery = f"""
                    SELECT
                        DISTINCT(cmt_commit_hash),
                        CASE WHEN contributors.cntrb_canonical IS NOT NULL THEN contributors.cntrb_canonical ELSE cmt_author_email END AS cntrb_canonical,
                        CASE WHEN canonical_full_names.cntrb_full_name IS NOT NULL THEN canonical_full_names.cntrb_full_name ELSE cmt_author_name END AS canonical_full_name,
                        cmt_author_name, cmt_author_email, repo_id, cmt_author_timestamp 
                    FROM commits 
                        LEFT OUTER JOIN contributors ON cntrb_email = cmt_author_email
                        LEFT OUTER JOIN (
                            SELECT cntrb_canonical, cntrb_full_name 
                            FROM contributors
                            WHERE cntrb_canonical = cntrb_email
                        ) canonical_full_names
                        ON canonical_full_names.cntrb_canonical = contributors.cntrb_canonical
                    WHERE
                        repo_id = {repo_id}
                        AND cmt_author_name NOT LIKE 'snyk%%'
                        AND cmt_author_name NOT LIKE '%%bot'
                        AND cmt_author_name != 'Spring Operator'
                        AND cmt_author_name != 'Spring Buildmaster'
                         AND cmt_author_timestamp >= {start_date}
                         AND cmt_author_timestamp <= {end_date}
                    ORDER BY
                        cntrb_canonical;
                    """
    
    commitsDF = pd.read_sql_query(commitsquery, con=engine)
    total_commits = commitsDF.cmt_commit_hash.nunique()    

    authorDF = pd.DataFrame()
    authorDF = commitsDF.canonical_full_name.value_counts()
    authorDF = authorDF.reset_index()
    authorDF.columns = ['name', 'commits']
    authorDF['percent'] = authorDF['commits'] / total_commits

    return authorDF

def output_filename(repo_name, repo_id, metric_string): 

    import datetime
    import pandas as pd
    from common_functions import augur_db_connect

    today = datetime.date.today()
    current_year_month = str(today.year) + '-' + '{:02d}'.format(today.month)

    # Get org_name
    engine = augur_db_connect()
    repo_info = pd.DataFrame()
    repo_info_query = f"""
                      SELECT repo_groups.rg_name from repo_groups, repo
                      WHERE 
                          repo.repo_id = {repo_id}
                          AND repo.repo_group_id = repo_groups.repo_group_id;
                     """
    repo_info = pd.read_sql_query(repo_info_query, con=engine)
    org_name = repo_info.rg_name[0]

    filename = 'output/' + repo_name + '_' + org_name + '_'  + metric_string + '_' + current_year_month + '.png'

    return filename

def contributor_risk(repo_id, repo_name, start_date, end_date, engine):

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
    
    names = [item[0] for item in risk_list]
    percents = [item[1] for item in risk_list]
    commits = [item[2] for item in risk_list]

    matplotlib.use('Agg') #prevents from tying to send plot to screen
    sns.set_style('ticks')
    sns.set(style="whitegrid", font_scale=2)

    fig, ax = plt.subplots()

    # the size of A4 paper
    fig.set_size_inches(24, 8)

    title = repo_name + "\nContributor Risk Metric Assessment: "

    if num_people < 3:
        risk = 'AT RISK'
        title += "AT RISK"
        title_color = 'firebrick'
    else:
        risk = 'HEALTHY'
        title += "Healthy"
        title_color = 'forestgreen'
    title += "\n" + str(num_people) + " people made up " + "{:.0%}".format(risk_percent) + " of the commits in the past year.\n"

    risk_bar = sns.barplot(x=names, y=commits, palette=bar_colors).set_title(title, fontsize=30, color=title_color)

    risk_bar_labels = ax.set_xticklabels(names, wrap=True)
    risk_bar_labels = ax.set_ylabel('Commits')
    risk_bar_labels = ax.set_xlabel('\nKey Contributors\n\nA healthy project should have at a minimum 3 people who combined account for the majority (>70%) of the commits.\nThe higher this number is, the more likely your project would succeed if a leading contributor suddenly left the project.\nRed bars indicate when less than 3 people have 70% of commits. Light blue for other contributors.')

    i = 0
    for p in ax.patches:
        ax.annotate("{:.0%}".format(percents[i]), (p.get_x() + p.get_width() / 2., p.get_height()),
            ha='center', va='center', color='gray', xytext=(0, 20),
            textcoords='offset points')
        i+=1

    filename = output_filename(repo_name, repo_id, 'contrib_risk_commits')

    fig.savefig(filename, bbox_inches='tight')
    plt.close(fig)

    print('\nContributor Risk for', repo_name, '\nfrom', start_date, 'to', end_date, '\nsaved as', filename)
    print(risk, '-', num_people, 'people make up > 70% of the commits in the past year\n')

    return num_people, risk

def response_time_data(repo_id, repo_name, start_date, end_date, engine):

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
                            count(*) FILTER (WHERE action = 'merged') AS merged_count,
                            MIN(message.msg_timestamp) AS first_response_time,
                            COUNT(DISTINCT message.msg_timestamp) AS comment_count,
                            MAX(message.msg_timestamp) AS last_response_time,
                            (MAX(message.msg_timestamp) - MIN(message.msg_timestamp)) / COUNT(DISTINCT message.msg_timestamp) AS average_time_between_responses
                            FROM pull_request_events, pull_requests, repo, pull_request_message_ref, message
                            WHERE repo.repo_id = {repo_id}
                            AND repo.repo_id = pull_requests.repo_id
                            AND pull_requests.pull_request_id = pull_request_events.pull_request_id
                            AND pull_requests.pull_request_id = pull_request_message_ref.pull_request_id
                            AND pull_request_message_ref.msg_id = message.msg_id
                            GROUP BY pull_requests.pull_request_id
                        ) response_times
                        ON pull_requests.pull_request_id = response_times.pull_request_id
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
                        ON base_labels.pull_request_id = all_commit_counts.pull_request_id
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
                        ON base_labels.pull_request_id = master_merged_counts.pull_request_id                    
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

def response_time(repo_id, repo_name, start_date, end_date, engine):

    import pandas as pd
    import seaborn as sns
    import matplotlib
    import matplotlib.pyplot as plt
    import datetime

    pr_all = response_time_data(repo_id, repo_name, start_date, end_date, engine)

    # Wrap in try except for projects with no PRs.
    try:
        pr_all['diff'] = pr_all.first_response_time - pr_all.pr_created_at
        pr_all['yearmonth'] = pr_all['pr_created_at'].dt.strftime('%Y-%m')
        pr_all['diff_days'] = pr_all['diff'] / datetime.timedelta(days=1)
    except:
        return -1, 'NO DATA'

    year_month_list = pr_all.yearmonth.unique()
    year_month_list.sort()

    # set bar colors red for high first response and blue for good
    first_response_median = pr_all.groupby(['repo_name', 'yearmonth'], as_index=False).median()[['repo_name', 'yearmonth', 'diff_days']]
    bar_colors = []
    k = 1
    risk_num = 0
    for med in first_response_median.diff_days:
        if med > 1:
            bar_colors.append('red')
            if k >= 6:
                risk_num+=1
        else:
            bar_colors.append('lightblue')
        k+=1

    # Start setting up plot configuration
    matplotlib.use('Agg') #prevents from tying to send plot to screen
    sns.set_style('ticks')
    sns.set(style="whitegrid", font_scale=2)

    fig, ax = plt.subplots()
    fig.set_size_inches(24, 8)

    # Color code title and indicate whether healthy or not
    title = repo_name + "\nTimely Responses:"

    if risk_num >= 2:
        risk = 'AT RISK'
        title += " AT RISK\n" + str(risk_num) + " months with median response times > 1 day in the past 6 months"
        title_color = 'firebrick'
    else:
        risk = 'HEALTHY'
        title += " Healthy\n" + str(risk_num) + "  month(s) with median first response times > 1 day in the past 6 months"
        title_color = 'forestgreen'

    my_plot = sns.boxplot(x='yearmonth', y='diff_days', palette=bar_colors, data=pr_all, ax=ax, order=year_month_list, showfliers = False, whis=3).set_title(title, fontsize=30, color=title_color)

    risk_bar_labels = ax.set_ylabel('First Response in Days')
    risk_bar_labels = ax.set_xlabel('Year-Month\n\nHealthy projects will have median first response times of about 1 day.\nThe median is indicated by the line contained within the bar.\nRed bars indicate median first response times > 1. Light blue for <= 1.')

    filename = output_filename(repo_name, repo_id, 'first_response_pr')

    fig.savefig(filename, bbox_inches='tight')
    plt.close(fig)

    print('\nTime to first response for', repo_name, '\nfrom', start_date, 'to', end_date, '\nsaved as', filename)
    print(risk, '-', risk_num, 'months have median response times of more than 1 day in the past 6 months\n')

    return risk_num, risk

def sustain_prs_by_repo(repo_id, repo_name, start_date, end_date, engine):

    import pandas as pd
    import seaborn as sns
    import matplotlib
    import matplotlib.pyplot as plt
    import datetime

    all_prsDF = monthly_prs_all(repo_id, repo_name, start_date, end_date, engine)

    # Return with no data if there are no PRs
    if all_prsDF['total_prs_open_closed'].sum() == 0:
        return -1, 'NO DATA'

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

    # the size of A4 paper
    fig.set_size_inches(24, 8)

    risk_num = 0
    h = 1
    for diff_per in pr_sustainDF['diff_per']:
        if (diff_per > 0.10 and h >=6):
            risk_num+=1
        h+=1

    title = pr_sustainDF['repo_name'][0] + "\nSustains and Keeps up with Contributions Metric:"

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

    filename = output_filename(repo_name, repo_id, 'sustains_pr')

    fig.savefig(filename, bbox_inches='tight')
    plt.close(fig)

    print('\nSustaining and keeping up with contributions for', repo_name, '\nfrom', start_date, 'to', end_date, '\nsaved as', filename)
    print(risk, '- Number of months in the past 6 months with > 10% of PRs not closed', risk_num, '\n')

    return risk_num, risk
