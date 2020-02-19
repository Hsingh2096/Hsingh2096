## Issue Open Hours   

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
        LEFT OUTER JOIN ( SELECT issue_id, ACTION, cntrb_id, created_at FROM issue_events WHERE ACTION = 'closed' OR ACTION = 'reopened' ORDER BY issue_id, issue_events.created_at DESC ) D ON issues.issue_id = d.issue_id,
        repo 
    WHERE
        issues.issue_id = D.issue_id 
        AND repo.repo_id = issues.repo_id 
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

### Working Notes
```sql
SELECT
    repo.repo_id,
    repo.repo_name,
    repo_groups.rg_name,
    AVG ( D.OPEN_DAYS ) AS average_open_days,
    MAX ( D.OPEN_DAYS ) AS max_open_days,
    MIN ( D.OPEN_DAYS ) AS min_open_days --,
    --stddev( D.OPEN_DAYS ) AS stddev_open_days 
FROM
    repo
    LEFT OUTER JOIN (
            SELECT
                repo.repo_id,
                issues.issue_id,
                COUNT ( issue_events.event_id ) as EVENT_COUNT,
                MAX ( issue_events.created_at ) AS LAST_EVENT_DATE,
                MAX ( issue_events.created_at )  - issues.created_at AS OPEN_DAYS 
            FROM
                issues,
                issue_events,
                repo 
            WHERE
                issues.repo_id = repo.repo_id 
                AND issues.issue_id = issue_events.issue_id 
                AND pull_request IS NULL 
                AND issues.issue_state = 'closed' 
            GROUP BY
                repo.repo_id, issues.issue_id 
                ORDER BY
                OPEN_DAYS DESC
            ) D on repo.repo_id = D.repo_id, 
            repo_groups
            group by 
                repo.repo_id,
    repo.repo_name,
        repo_groups.rg_name


-- second edition 

            SELECT
                repo.repo_id,
                issues.issue_id,
                COUNT ( issue_events.event_id ) as EVENT_COUNT,
                MAX ( issue_events.created_at ) AS LAST_EVENT_DATE,
                MAX( issue_events.created_at ) - issues.created_at AS OPEN_DAYS 
            FROM
                issues,
                issue_events,
                repo 
            WHERE
                issues.repo_id = repo.repo_id 
                AND issues.issue_id = issue_events.issue_id 
                AND pull_request IS NULL 
                AND issues.issue_state = 'closed' 
            GROUP BY
                repo.repo_id, issues.issue_id 
                ORDER BY
                OPEN_DAYS DESC;
                
                
                select count(issue_id) from issues; 
                
SELECT
    repo_id,
    issue_id,
    event_action,
    cntrb_id,
    --extract(hours from TIMESTAMP event_created_at - TIMESTAMP issue_created_at)) as hours_to_close, 
    -- DATE_DIFF('hour', event_created_at - event_created_at ) AS hours_to_close, 
    min((EXTRACT(EPOCH FROM event_created_at)) - EXTRACT(EPOCH FROM issue_created_at))/3600 as hours_to_first_close, 
    max((EXTRACT(EPOCH FROM event_created_at)) - EXTRACT(EPOCH FROM issue_created_at))/3600 as hours_to_final_close
    --event_created_at - issue_created_at AS time_to_close, 
  --EXTRACT(EPOCH FROM event_created_at)    
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
        LEFT OUTER JOIN ( SELECT issue_id, ACTION, cntrb_id, created_at FROM issue_events WHERE ACTION = 'closed' OR ACTION = 'reopened' ORDER BY issue_id, issue_events.created_at DESC ) D ON issues.issue_id = d.issue_id,
        repo 
    WHERE
        issues.issue_id = D.issue_id 
        AND repo.repo_id = issues.repo_id 
    ORDER BY
        repo.repo_id,
        issues.issue_id,
        event_created_at DESC 
    ) P
    group by p.repo_id, p.issue_id, p.event_action, p.cntrb_id;
    
    select extract(hours from TIMESTAMP(
                
                select distinct action from issue_events order by action; 


```
								
	