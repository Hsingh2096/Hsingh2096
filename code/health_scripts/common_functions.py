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
                        CASE WHEN contributors.cntrb_canonical IS NOT NULL THEN contributors.cntrb_canonical ELSE cmt_author_email END AS cntrb_canonical,
                        CASE WHEN canonical_full_names.cntrb_full_name IS NOT NULL THEN canonical_full_names.cntrb_full_name ELSE cmt_author_name END AS canonical_full_name,
                        cmt_author_name, cmt_author_email, repo_id, cmt_id, cmt_author_timestamp 
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
    total_commits = commitsDF.cmt_id.nunique()    

    authorDF = pd.DataFrame()
    authorDF = commitsDF.canonical_full_name.value_counts()
    authorDF = authorDF.reset_index()
    authorDF.columns = ['name', 'commits']
    authorDF['percent'] = authorDF['commits'] / total_commits
    print(authorDF.head(10))

    return authorDF

def output_filename(repo_name, metric_string): 

    import datetime

    today = datetime.date.today()
    current_year_month = str(today.year) + '-' + '{:02d}'.format(today.month)

    filename = 'output/' +  metric_string + '_' + repo_name + "_" + current_year_month + '.png'

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
    
        if (cum_percent > .50 and num_people == 0):
            num_people = i
            risk_percent = cum_percent
        
        if i == 8:
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
            bar_colors.append('blue')
    
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
        title += "AT RISK"
        title_color = 'firebrick'
    else:
        title += "Healthy"
        title_color = 'forestgreen'
    title += "\n" + str(num_people) + " people made up " + "{:.0%}".format(risk_percent) + " of the commits in the past year.\n"

    risk_bar = sns.barplot(x=names, y=commits, palette=bar_colors).set_title(title, fontsize=30, color=title_color)

    risk_bar_labels = ax.set_xticklabels(names, wrap=True)
    risk_bar_labels = ax.set_ylabel('Commits')
    risk_bar_labels = ax.set_xlabel('\nKey Contributors\n\nA healthy project should have at a minimum 3 people who combined account for the majority (>50%) of the commits.\nThe higher this number is, the more likely your project would succeed if a leading contributor suddenly left the project.')

    i = 0
    for p in ax.patches:
        ax.annotate("{:.0%}".format(percents[i]), (p.get_x() + p.get_width() / 2., p.get_height()),
            ha='center', va='center', color='gray', xytext=(0, 20),
            textcoords='offset points')
        i+=1

    filename = output_filename(repo_name, 'contrib_risk_commits')

    fig.savefig(filename, bbox_inches='tight')

    print('\nContributor Risk for', repo_name, '\nfrom', start_date, 'to', end_date, '\nsaved as', filename, '\n')

def sustain_prs_by_repo(repo_id, repo_name, start_date, end_date, engine):

    import pandas as pd
    import seaborn as sns
    import matplotlib
    import matplotlib.pyplot as plt
    import datetime

    closed_prsDF = monthly_prs_closed(repo_id, repo_name, start_date, end_date, engine)
    all_prsDF = monthly_prs_all(repo_id, repo_name, start_date, end_date, engine)

    pr_sustainDF = pd.DataFrame()

    pr_sustainDF['yearmonth'] = closed_prsDF['yearmonth']
    pr_sustainDF['repo_name'] = closed_prsDF['repo_name']
    pr_sustainDF['repo_id'] = closed_prsDF['repo_id']
    pr_sustainDF['closed_total'] = closed_prsDF['total_prs_open_closed']

    pr_sustainDF['all_total'] = all_prsDF['total_prs_open_closed']
    pr_sustainDF['diff'] = pr_sustainDF['all_total'] - pr_sustainDF['closed_total']

    # Disply results on a graph
    pr_sustainDF['repo_id'] = pr_sustainDF['repo_id'].map(int)
    pr_sustainDF.set_index('repo_id', 'yearmonth')

    matplotlib.use('Agg') #prevents from tying to send plot to screen
    sns.set_style('ticks')
    sns.set(style="whitegrid", font_scale=2)

    fig, ax = plt.subplots()

    # the size of A4 paper
    fig.set_size_inches(24, 8)

    title = pr_sustainDF['repo_name'][0] + "\nSustains and Keeps up with Contributions Metric\nTotal vs Closed Pull Request Comparison"

    plottermonth = sns.lineplot(x='yearmonth', y='all_total', data=pr_sustainDF, sort=False, color='black', label='Total', linewidth=2.5)
    plottermonth = sns.lineplot(x='yearmonth', y='closed_total', data=pr_sustainDF, sort=False, color='green', label='Closed', linewidth=2.5, linestyle='dashed').set_title(title, fontsize=30) 

    plottermonthlabels = ax.set_xticklabels(pr_sustainDF['yearmonth'])
    plottermonthlabels = ax.set_ylabel('Number of PRs')
    plottermonthlabels = ax.set_xlabel('Year Month\n\nInterpretation: Healthy projects will have little or no gap. A large or increasing gap requires attention.')

    filename = output_filename(repo_name, 'sustains_pr')

    fig.savefig(filename, bbox_inches='tight')

    print('\nSustaining and keeping up with contributions for', repo_name, '\nfrom', start_date, 'to', end_date, '\nsaved as', filename, '\n')
