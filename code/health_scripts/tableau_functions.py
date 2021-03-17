#OBSOLETE - This script has been moved to the Jupyter Notebook: OSPO_Project_Health_Data_Tableau.ipynb



def sustain_prs_by_repo_tableau(repo_id, repo_name, org_name, start_date, end_date, engine):

    import pandas as pd
    from common_functions import sustain_prs_by_repo_data 
    # Delete import below after testing
    from common_functions import sustain_prs_by_repo_graph

    error_num, error_text, pr_sustainDF, title, title_color, interpretation, risk, risk_num = sustain_prs_by_repo_data(repo_id, repo_name, org_name, start_date, end_date, engine)

    # error_num == 0 - ok to generate graph. If error_num == -1, there aren't enough PRs to generate the graph.
    # pr_sustainDF: is the dataframe containing the data you need to graph
    # title: this is the title for the top of the chart
    # title_color: The title text should be displayed in this color
    # interpretation: This text should appear at the bottom of the graph
    # risk and risk num: You can ignore these variables

    if error_num == 0:
        # Add code here to generate what you need for Tableau. 

        # for testing and validation below. You can delete the lines below when you start generating yours graphs
        # this creates my .png chart, and you might want to look at it to see how I've accessed the dataframe. 
        sustain_risk_num, sustain_risk = sustain_prs_by_repo_graph(repo_id, repo_name, org_name, start_date, end_date, engine)
        # print the dataframe so that you know what you have
        print('Sustain Dataframe\n', pr_sustainDF, '\n\n')


def contributor_risk_tableau(repo_id, repo_name, org_name, start_date, end_date, engine):

    from common_functions import contributor_risk_data
    # Delete import below after testing
    from common_functions import contributor_risk_graph

    error_num, error_text, names, percents, commits, bar_colors, title, title_color, interpretation, risk, num_people = contributor_risk_data(repo_id, repo_name, org_name, start_date, end_date, engine)

    # names, percents, commits, bar_colors are all lists containing what you would expect.
    # The sequences of the lists are important. percents[0], commits[0], bar_colors[0] contain the data for names[0] 

    if error_num == 0:
        # Add code here to generate what you need for Tableau. 

        # for testing and validation below. You can delete the lines below when you start generating yours graphs
        # this creates my .png chart, and you might want to look at it to see how I've accessed the dataframe. 
        contrib_risk_num, contrib_risk = contributor_risk_graph(repo_id, repo_name, org_name, start_date, end_date, engine)
        # print the data so that you know what you have
        print('Names', names)
        print('Percents', percents)
        print('Commits', commits)
        print('Bar_colors', bar_colors)


def response_time_tableau(repo_id, repo_name, org_name, start_date, end_date, engine):

    import pandas as pd
    from common_functions import response_time_data
    # Delete import below after testing
    from common_functions import response_time_graph

    error_num, error_text, pr_responseDF, title, title_color, interpretation, risk, risk_num = response_time_data(repo_id, repo_name, org_name, start_date, end_date, engine)

    # pr_responseDF['total_prs'] is the black line in my chart representing 'Total'.
    # pr_responseDF['in_guidelines'] is the green line representing 'Response < 2 business days'

    if error_num == 0:
        # Add code here to generate what you need for Tableau. 

        # for testing and validation below. You can delete the lines below when you start generating yours graphs
        # this creates my .png chart, and you might want to look at it to see how I've accessed the dataframe. 
        response_risk_num, response_risk = response_time_graph(repo_id, repo_name, org_name, start_date, end_date, engine)
        # print the dataframe so that you know what you have
        print('Response Time Dataframe\n', pr_responseDF, '\n\n')

def activity_release_tableau(repo_name, org_name, start_date, end_date, repo_api):

    ### IMPORTANT: You need to have a GitHub API key stored in a file named gh_key in the same directory as this NB

    import pandas as pd
    from common_functions import activity_release_data
    # Delete import below after testing
    from common_functions import activity_release_graph

    error_num, error_text, releasesDF, start_dt, end_dt, title, title_color, interpretation, risk, risk_num = activity_release_data(repo_name, org_name, start_date, end_date, repo_api)

    # releasesDF['date'] is what should be plotted with x's or similar at the appropriate date on the x axis

    if error_num == 0:
        # Add code here to generate what you need for Tableau. 

        # for testing and validation below. You can delete the lines below when you start generating yours graphs
        # this creates my .png chart, and you might want to look at it to see how I've accessed the dataframe. 
        release_risk_num, release_risk = activity_release_graph(repo_name, org_name, start_date, end_date, repo_api)
        # print the dataframe so that you know what you have
        print('Releases Dataframe\n', releasesDF, '\n\n')

