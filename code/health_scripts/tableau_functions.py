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

    print('contributor_risk_tableau not implemented yet')

def response_time_tableau(repo_id, repo_name, org_name, start_date, end_date, engine):

    print('response_time_tableau not implemented yet')

def activity_release_tableau(repo_name, org_name, start_date, end_date, repo_api):

    print('activity_release_tableau not implemented yet')
