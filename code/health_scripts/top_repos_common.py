def get_commits_by_repo(start_date, end_date, engine):
    import pandas as pd

    repo_list_commits = pd.DataFrame()
    repo_list_commits_query = f"""
            SELECT COUNT(DISTINCT commits.cmt_commit_hash), repo.repo_id, repo.repo_name, repo.repo_path from repo, commits
            WHERE 
                repo.repo_id = commits.repo_id
                AND commits.cmt_author_timestamp >= {start_date}
                AND commits.cmt_author_timestamp <= {end_date}
            GROUP BY repo.repo_id
            ORDER BY COUNT(DISTINCT commits.cmt_commit_hash);
            """
    repo_list_commits = pd.read_sql_query(repo_list_commits_query, con=engine)

    return repo_list_commits
