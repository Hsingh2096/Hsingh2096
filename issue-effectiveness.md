# Effectiveness in Quickly Resolving Software Issues

## Goal
To understand how effective a community is in the resolution of software issues

## Question(s)
1. How and to what extent does the community participate in the resolution of software issues?
2. How quickly are software issues resolved?  
3. How quickly are new pull requests resolved? 
4. What is the ratio of pull requests made to pull requests accepted? 

## Metrics: Issues 

### Community Participation in Issues
One measure of community participation in issue resolution is the amount of conversation that occurs around issues themselves. 

1. This query describes the total number of issues opened in a repository, and the average, maximum and minimum number of comments on an issue. [Results from December 1, 2019 are here.](./results/issues-and-issue-comments.csv)
```sql
    SELECT
        repo.repo_id,
        repo.repo_name,
        repo_groups.rg_name,
        E.issues_count,
        AVG ( D.comment_count ) AS average_comments,
        MAX ( D.comment_count ) AS max_comments,
        MIN ( D.comment_count ) AS min_comments,
        stddev( D.comment_count ) AS stddev_comments 
    FROM
        repo
        LEFT OUTER JOIN (
        SELECT
            issues.issue_id,
            issues.repo_id,
            COUNT ( K.issue_msg_ref_id ) AS comment_count 
        FROM
            issues
            LEFT OUTER JOIN issue_message_ref K ON issues.issue_id = K.issue_id 
        WHERE
            pull_request IS NULL -- GitHub provides pull requests in their issues API, as well as their pull requests API. We do not exclude this data from collection because it would make the provenance of the data we collect less transparent. We apply filters in queries and API endpoints, but not collection.
            
        GROUP BY
            issues.issue_id,
            issues.repo_id 
        ORDER BY
            issues.repo_id 
        ) D ON repo.repo_id = D.repo_id,
        repo_groups,
        ( -- subquery table to provide issues count in context 
        SELECT
            repo.repo_id,
            COUNT ( issue_id ) AS issues_count 
        FROM
            repo
            LEFT OUTER JOIN (
            SELECT
                repo.repo_id,
                issues.issue_id --the "double left outer join here seems puzzling. TO preserve "one row per repo" and exclude pull requests, we FIRST need to get a list of issues that are not pull requests, then count those. WIthout the "double left outer join", we would exclude repos that use pull requests, but not issues on GitHub
                
            FROM
                repo
                LEFT OUTER JOIN issues ON issues.repo_id = repo.repo_id 
            WHERE
                issues.pull_request IS NULL -- here again, excluding pull_requests at data analysis, but preserving GitHub API Provenance
                
            ) K ON repo.repo_id = K.repo_id 
        GROUP BY
            repo.repo_id 
        ) E -- this subquery table is what gives us the issue count per repo as context for deciding if repos with very small issue counts are excluded from some analyses.
        
    WHERE
        repo.repo_group_id = repo_groups.repo_group_id 
        AND repo.repo_id = E.repo_id 
    GROUP BY
        repo.repo_id,
        repo.repo_name,
        repo_groups.rg_name,
        repo_groups.repo_group_id,
        E.issues_count 
    ORDER BY
        rg_name,
        repo_name;
```
2. This query calculates statistics about the number of specific people involved in each issue by counting the distinct contributor ids for each issue first, then summarizing. [Results from December 1, 2019 are here.](./results/repo-issues-contributors-summary-stats.csv)
```sql
    SELECT
        repo.repo_id,
        repo.repo_name,
        repo_groups.rg_name,-- we provide repo group name, but also group by the repo group ID ... just in case you name two repo groups the same thing
        E.issues_count,-- providing the number of issues primarily as context: very low issue counts may best be excluded
        AVG ( s.issue_contributors ) AS average_issue_contributors,
        MAX ( s.issue_contributors ) AS max_issue_contributors,
        MIN ( s.issue_contributors ) AS min_issue_contributors,
        stddev( s.issue_contributors ) AS stddev_issue_contributors 
    FROM
        repo -- by selecting from repo and then left outer joining on the query with the raw stats per issue, we get one record per repository, even if that repository does not have issues on GitHub (or other issue tracker Augur collects from)
        LEFT OUTER JOIN ( -- begin, major left outer join 
        SELECT
            repo_id,
            issue_id,
            COUNT ( contributor ) AS issue_contributors 
        FROM
            (
            SELECT
                repo_id,
                issue_id,
                cntrb_id AS contributor 
            FROM
                (
                SELECT
                    repo.repo_id AS repo_id,
                    issues.issue_id AS issue_id,
                    ACTION AS event_action,
                    D.cntrb_id 
                FROM
                    issues
                    LEFT OUTER JOIN ( SELECT issue_id, ACTION, cntrb_id, created_at FROM issue_events ORDER BY issue_id, issue_events.created_at DESC ) D ON issues.issue_id = d.issue_id,
                    repo 
                WHERE
                    issues.issue_id = D.issue_id 
                    AND repo.repo_id = issues.repo_id 
                    AND issues.pull_request IS NULL -- GitHub provides pull requests in their issues API, as well as their pull requests API. We do not exclude this data from collection because it would make the provenance of the data we collect less transparent. We apply filters in queries and API endpoints, but not collection.
                    
                ORDER BY
                    repo.repo_id,
                    issues.issue_id 
                ) P 
            GROUP BY
                P.repo_id,
                P.issue_id,
                P.cntrb_id 
                
            UNION-- here we are counting the person who CREATES the issue, as well as each EVENT CREATOR as a contributor (query below for issue creators)
            
            SELECT
                repo_id,
                issue_id,
                cntrb_id AS contributor 
            FROM
                issues 
            WHERE
                issues.pull_request IS NULL -- exclusion of pull request data at analysis time, preservation of provenance.
                
            ORDER BY
                repo_id,
                issue_id,
                contributor 
            ) x 
        GROUP BY
            repo_id,
            issue_id 
        ) s ON repo.repo_id = s.repo_id, -- END, major left outer join 
        repo_groups, -- also including repo_groups table for repo group names in result 
        (
        SELECT
            repo.repo_id,
            COUNT ( issue_id ) AS issues_count 
        FROM
            repo
            LEFT OUTER JOIN (
            SELECT
                repo.repo_id,
                issues.issue_id --the "double left outer join here seems puzzling. TO preserve "one row per repo" and exclude pull requests, we FIRST need to get a list of issues that are not pull requests, then count those. WIthout the "double left outer join", we would exclude repos that use pull requests, but not issues on GitHub
                
            FROM
                repo
                LEFT OUTER JOIN issues ON issues.repo_id = repo.repo_id 
            WHERE
                issues.pull_request IS NULL -- here again, excluding pull_requests at data analysis, but preserving GitHub API Provenance
                
            ) K ON repo.repo_id = K.repo_id 
        GROUP BY
            repo.repo_id 
        ) E -- this subquery table is what gives us the issue count per repo as context for deciding if repos with very small issue counts are excluded from some analyses.
        
    WHERE
        repo.repo_group_id = repo_groups.repo_group_id
        AND repo.repo_id = E.repo_id 

    GROUP BY
        repo.repo_id,
        repo.repo_name,
        repo_groups.rg_name,
        repo_groups.repo_group_id,
        E.issues_count -- This looks odd at first. We are getting the issue count from a subquery, and its selected for context, so "by law" we have to group by it. Ordinarily grouping by a "count" seems to violate set logic. In this case, set logic is preserved by the "E" table's left outer join on repo, which ensures that we have an issue count row for every repo and only every repo, regardless of whether or not it has any issues in GitHub
        
    ORDER BY
        rg_name,
        repo.repo_name;
```

### How Quickly Issues are Closed in a Community 

1. This query calculates the time it takes for each issue to be closed the first time, and the final time. [Results from December 1, 2019 are here.](./results/issue-time-to-close-each-closed-issue.csv). This query can be used as a "base" for performing different types of summarization, since it includes every closed issue's hours to first close and hours to final close. **You can use this granular query as a model for generating counts of a number of different statistics, and then the next query as a model for how you would summarize the granular data.** 
```sql
-- Issues can be opened, closed, reopened, then closed again. This query gives you two totals in 
-- hours. One between the issue creation date and the first close, and the second between the issue creation 
-- date and the final close. If an issue is reopened multiple times, and you wanted to understand that data, 
-- you would need to write an iterator in R or Python 
    SELECT
        repo_id,
        issue_id,
        cntrb_id,
        MIN ((
            EXTRACT ( EPOCH FROM event_created_at )) - EXTRACT ( EPOCH FROM issue_created_at )) / 3600 AS hours_to_first_close,
        MAX ((
            EXTRACT ( EPOCH FROM event_created_at )) - EXTRACT ( EPOCH FROM issue_created_at )) / 3600 AS hours_to_final_close 
    FROM
        (
        SELECT
            repo.repo_id AS repo_id,
            issues.issue_id AS issue_id,
            ACTION AS event_action,
            D.cntrb_id AS cntrb_id,
            issues.created_at AS issue_created_at,
            D.created_at AS event_created_at 
        FROM
            issues
            LEFT OUTER JOIN 
                ( SELECT issue_id, ACTION, cntrb_id, created_at 
                FROM issue_events 
                WHERE ACTION = 'closed' OR ACTION = 'reopened' 
                ORDER BY issue_id, issue_events.created_at DESC ) D ON issues.issue_id = d.issue_id,
            repo 
        WHERE
            issues.issue_id = D.issue_id 
            AND repo.repo_id = issues.repo_id 
            AND issues.pull_request IS NULL -- exclude pull requests in issue analysis; preserve the provenance, because GitHub gives you pull requests as issues in the issues API. To look only at Pull Requests, there is a separate pull request API set of endpoints, where we store data in pull_requests tables. 
        ORDER BY
            repo.repo_id,
            issues.issue_id,
            event_created_at DESC 
        ) P 
    GROUP BY
        P.repo_id,
        P.issue_id,
        P.cntrb_id;
```
2. This query summarizes the average, min, max, and standard deviation of "time to close" for issues opened in a repository that are currently closed. [Results from December 1, 2019 are here.](./results/repo_issue_time_to_close_summary_stats_all.csv)   
```sql
-- You can then take this SQL calculate basic statistics across each repository
    SELECT
        repo.repo_id,
        repo.repo_name,
        repo.repo_group_id,
        repo_groups.rg_name,
        AVG ( D.hours_to_first_close ) AS average_hours_to_first_close,
        MAX ( D.hours_to_first_close ) AS max_hours_to_first_close,
        MIN ( D.hours_to_first_close ) AS min_hours_to_first_close,
        stddev( D.hours_to_first_close ) AS stddev_hours_to_first_close,
        AVG ( D.hours_to_final_close ) AS average_hours_to_final_close,
        MAX ( D.hours_to_final_close ) AS max_hours_to_final_close,
        MIN ( D.hours_to_final_close ) AS min_hours_to_final_close,
        stddev( D.hours_to_final_close ) AS stddev_hours_to_final_close 
    FROM
        repo -- we are using repo as our base for summarization
        LEFT OUTER JOIN (-- BEGIN major left outer join ... the left outer join on the query showing the details will give us a row for every repository, even if there are no issue records.
             SELECT
                repo_id,
                issue_id,
                cntrb_id,
                MIN ((
                    EXTRACT ( EPOCH FROM event_created_at )) - EXTRACT ( EPOCH FROM issue_created_at )) / 3600 AS hours_to_first_close,
                MAX ((
                    EXTRACT ( EPOCH FROM event_created_at )) - EXTRACT ( EPOCH FROM issue_created_at )) / 3600 AS hours_to_final_close 
            FROM
                (
                SELECT
                    repo.repo_id AS repo_id,
                    issues.issue_id AS issue_id,
                    ACTION AS event_action,
                    D.cntrb_id AS cntrb_id,
                    issues.created_at AS issue_created_at,
                    D.created_at AS event_created_at 
                FROM
                    issues
                    LEFT OUTER JOIN 
                        ( SELECT issue_id, ACTION, cntrb_id, created_at 
                        FROM issue_events 
                        WHERE ACTION = 'closed' OR ACTION = 'reopened' 
                        ORDER BY issue_id, issue_events.created_at DESC ) D ON issues.issue_id = d.issue_id,
                    repo 
                WHERE
                    issues.issue_id = D.issue_id 
                    AND repo.repo_id = issues.repo_id 
                    AND issues.pull_request IS NULL -- exclude pull requests in issue analysis; preserve the provenance, because GitHub gives you pull requests as issues in the issues API. To look only at Pull Requests, there is a separate pull request API set of endpoints, where we store data in pull_requests tables. 
                ORDER BY
                    repo.repo_id,
                    issues.issue_id,
                    event_created_at DESC 
                ) P 
            GROUP BY
                P.repo_id,
                P.issue_id,
                P.cntrb_id
        ) D ON repo.repo_id = D.repo_id, -- END major left outer join 
        repo_groups -- adding repo_groups allows us to do summarizations at that level more easily if we want.
        
    WHERE
        repo.repo_group_id = repo_groups.repo_group_id --if we do not create this join condition, then we get a cartesian product. Specifically, we will have a row for every repository and repository group combination, although logically that makes no sense. Effectively you get a number of rows that is the product of the row counts in (repo * repo_groups)
        
    GROUP BY
        repo.repo_id,
        repo.repo_name,
        repo.repo_group_id,
        repo_groups.rg_name;
```

## Metrics: Resolution of Pull Requests 


### Pull Request Resolution Time



### Pull Request Acceptance Rate
