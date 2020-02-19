# Committer Count Fix

The committer count API was returning the total commits, NOT the total committers. 

## Broke SQL Block
```python
    if repo_id:
        committersSQL = s.sql.text(
            """
                SELECT
                    date_trunc(:period, commits.cmt_author_date::date) as date,
                    repo_name,
                    rg_name,
                    count(cmt_author_name)
                FROM
                    commits, repo, repo_groups
                WHERE
                    commits.repo_id = :repo_id AND commits.repo_id = repo.repo_id
                    AND repo.repo_group_id = repo_groups.repo_group_id
                    AND commits.cmt_author_date BETWEEN :begin_date and :end_date
                GROUP BY date, repo_name, rg_name
                ORDER BY date DESC
            """
        )
    else:
        committersSQL = s.sql.text(
            """
            SELECT
                date_trunc(:period, commits.cmt_author_date::date) as date,
                rg_name,
                count(cmt_author_name)
            FROM
                commits, repo, repo_groups
            WHERE
                repo.repo_group_id = repo_groups.repo_group_id AND repo.repo_group_id = :repo_group_id
                AND repo.repo_id = commits.repo_id
                AND commits.cmt_author_date BETWEEN :begin_date and :end_date
            GROUP BY date, rg_name
            """
        )

    results = pd.read_sql(committersSQL, self.database, params={'repo_id': repo_id, 
        'repo_group_id': repo_group_id,'begin_date': begin_date, 'end_date': end_date, 'period':period})

    return results

```

## Fixed SQL with example (by repo): 
```sql
SELECT DATE,
	repo_name,
	rg_name,
	COUNT ( author_count ) 
FROM
	(
	SELECT
		date_trunc( 'month', commits.cmt_author_timestamp AT TIME ZONE'America/Chicago' ) AS DATE,
		repo_name,
		rg_name,
		cmt_author_name,
		cmt_author_email,
		COUNT ( cmt_author_email ) AS author_count 
	FROM
		commits,
		repo,
		repo_groups 
	WHERE
		commits.repo_id = 25158 
		AND commits.repo_id = repo.repo_id 
		AND repo.repo_group_id = repo_groups.repo_group_id 
		AND commits.cmt_author_timestamp AT TIME ZONE'America/Chicago' BETWEEN '2019-11-01' 
		AND '2019-11-30' 
	GROUP BY
		DATE,
		repo_name,
		rg_name,
		cmt_author_name,
		cmt_author_email 
	ORDER BY
		DATE,
		cmt_author_name,
		cmt_author_email 
	) C 
GROUP BY
	C.DATE,
	repo_name,
	rg_name
```

## Fixed SQL with example (by repo group):
```sql
SELECT DATE,
    rg_name,
    COUNT ( author_count ) 
FROM
    (
    SELECT
        date_trunc( 'month', commits.cmt_author_timestamp AT TIME ZONE'America/Chicago' ) AS DATE,
        rg_name,
        cmt_author_name,
        cmt_author_email,
        COUNT ( cmt_author_email ) AS author_count 
    FROM
        commits,
        repo,
        repo_groups 
    WHERE
        commits.repo_id = repo.repo_id 
        AND repo.repo_group_id = repo_groups.repo_group_id 
        AND commits.cmt_author_timestamp AT TIME ZONE'America/Chicago' BETWEEN '2019-11-01' 
        AND '2019-11-30' 
        AND repo.repo_group_id = 25151
    GROUP BY
        DATE,
        rg_name,
        cmt_author_name,
        cmt_author_email 
    ORDER BY
        DATE,
        cmt_author_name,
        cmt_author_email 
    ) C 
GROUP BY
    C.DATE,
    rg_name
order by c.date desc; 
```

## Fixed Python
```python 
if repo_id:
    committersSQL = s.sql.text(
        """
            SELECT DATE,
                repo_name,
                rg_name,
                COUNT ( author_count ) 
            FROM
                (
                SELECT
                    date_trunc(:period, commits.cmt_author_date::date) as date,
                    repo_name,
                    rg_name,
                    cmt_author_name,
                    cmt_author_email,
                    COUNT ( cmt_author_name ) AS author_count 
                FROM
                    commits, repo, repo_groups
                WHERE
                    commits.repo_id = :repo_id AND commits.repo_id = repo.repo_id
                    AND repo.repo_group_id = repo_groups.repo_group_id
                    AND commits.cmt_author_date BETWEEN :begin_date and :end_date
                GROUP BY date, repo_name, rg_name, cmt_author_name, cmt_author_email 
                ORDER BY date DESC
                ) C
            GROUP BY
                C.DATE,
                repo_name,
                rg_name 
            ORDER BY C.DATE desc 
        """
    )
else:
    committersSQL = s.sql.text(
        """
            SELECT DATE,
                rg_name,
                COUNT ( author_count ) 
            FROM
                (
                SELECT
                    date_trunc(:period, commits.cmt_author_date::date) as date,
                    rg_name,
                    cmt_author_name,
                    cmt_author_email,
                    COUNT ( cmt_author_name ) AS author_count 
                FROM
                    commits, repo, repo_groups
                WHERE
                    commits.repo_id = repo.repo_id
                    AND repo.repo_group_id = repo_groups.repo_group_id
                    AND commits.cmt_author_date BETWEEN :begin_date and :end_date
                    AND repo.repo_group_id = :repo_group_id
                GROUP BY date, rg_name, cmt_author_name, cmt_author_email 
                ORDER BY date DESC
                ) C
            GROUP BY
                C.DATE,
                rg_name 
            ORDER BY C.DATE desc 
        """
```

## Old REPO GROUP Python for checking 
```python 
            SELECT
                date_trunc(:period, commits.cmt_author_date::date) as date,
                rg_name,
                count(cmt_author_name)
            FROM
                commits, repo, repo_groups
            WHERE
                repo.repo_group_id = repo_groups.repo_group_id AND repo.repo_group_id = :repo_group_id
                AND repo.repo_id = commits.repo_id
                AND commits.cmt_author_date BETWEEN :begin_date and :end_date
            GROUP BY date, rg_name
            """
        )

    results = pd.read_sql(committersSQL, self.database, params={'repo_id': repo_id, 
        'repo_group_id': repo_group_id,'begin_date': begin_date, 'end_date': end_date, 'period':period})

    return results
```

