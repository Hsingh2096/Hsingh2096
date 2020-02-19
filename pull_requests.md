# Pull Requests
## Pull request effectiveness 
```sql
    SELECT
        repo_id,
        pull_request_id,
        cntrb_id,
        MIN ((
            EXTRACT ( EPOCH FROM event_created_at )) - EXTRACT ( EPOCH FROM pr_created_at )) / 3600 AS hours_to_first_close,
        MAX ((
            EXTRACT ( EPOCH FROM event_created_at )) - EXTRACT ( EPOCH FROM pr_created_at )) / 3600 AS hours_to_final_close 
    FROM
        (
        SELECT
            repo.repo_id AS repo_id,
            pull_requests.pull_request_id AS pull_request_id,
            ACTION AS event_action,
            D.cntrb_id AS cntrb_id,
            pull_requests.pr_created_at AS pr_created_at,
            D.created_at AS event_created_at 
        FROM
            pull_requests
            LEFT OUTER JOIN 
                ( SELECT pull_request_id, ACTION, cntrb_id, created_at 
                FROM pull_request_events 
                WHERE ACTION = 'closed' OR ACTION = 'reopened' 
                ORDER BY pull_request_id, pull_request_events.created_at DESC ) D ON pull_requests.pull_request_id = D.pull_request_id,
            repo 
        WHERE
            pull_requests.pull_request_id = D.pull_request_id 
            AND repo.repo_id = pull_requests.repo_id 
        ORDER BY
            repo.repo_id,
            pull_requests.pull_request_id,
            event_created_at DESC 
        ) P 
    GROUP BY
        P.repo_id,
        P.pull_request_id,
        P.cntrb_id;
```

## Pull Request Reopen Rate
```sql
select * from (
SELECT
        repo_id,
        pull_request_id,
        cntrb_id,
        MIN ((
            EXTRACT ( EPOCH FROM event_created_at )) - EXTRACT ( EPOCH FROM pr_created_at )) / 3600 AS hours_to_first_close,
        MAX ((
            EXTRACT ( EPOCH FROM event_created_at )) - EXTRACT ( EPOCH FROM pr_created_at )) / 3600 AS hours_to_final_close 
    FROM
        (
        SELECT
            repo.repo_id AS repo_id,
            pull_requests.pull_request_id AS pull_request_id,
            ACTION AS event_action,
            D.cntrb_id AS cntrb_id,
            pull_requests.pr_created_at AS pr_created_at,
            D.created_at AS event_created_at 
        FROM
            pull_requests
            LEFT OUTER JOIN 
                ( SELECT pull_request_id, ACTION, cntrb_id, created_at 
                FROM pull_request_events 
                WHERE ACTION = 'merged' -- OR ACTION = 'reopened' 
                ORDER BY pull_request_id, pull_request_events.created_at DESC ) D ON pull_requests.pull_request_id = D.pull_request_id,
            repo 
        WHERE
            pull_requests.pull_request_id = D.pull_request_id 
            AND repo.repo_id = pull_requests.repo_id 
        ORDER BY
            repo.repo_id,
            pull_requests.pull_request_id,
            event_created_at DESC 
        ) P 
    GROUP BY
        P.repo_id,
        P.pull_request_id,
        P.cntrb_id
        ) X where X.hours_to_first_close != x.hours_to_final_close; 
```

