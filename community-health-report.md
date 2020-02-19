# Community health report queries

## Pull Request Time to Close

```sql
SELECT
    * 
FROM
    (
    SELECT
        date_part( 'year', week :: DATE ) AS YEAR,
        date_part( 'week', week :: DATE ) AS week 
    FROM
        ( SELECT * FROM ( SELECT week :: DATE FROM generate_series ( TIMESTAMP '2013-01-01', TIMESTAMP '2020-01-30', INTERVAL '1 week' ) week ) d ) x 
    ) y
    LEFT OUTER JOIN (
    SELECT
        repo_id,
        repo_name,
        repo_group,
        date_part( 'year', pr_created_at :: DATE ) AS YEAR,
        date_part( 'week', pr_created_at :: DATE ) AS week,
        AVG ( hours_to_close ) AS wk_avg_hours_to_close,
        AVG ( days_to_close ) AS wk_avg_days_to_close,
        COUNT ( pr_src_id ) AS total_prs_open_closed 
    FROM
        (
        SELECT
            repo.repo_id AS repo_id,
            repo.repo_name AS repo_name,
            repo_groups.rg_name AS repo_group,
            pull_requests.pr_created_at AS pr_created_at,
            pull_requests.pr_closed_at AS pr_closed_at,
            pull_requests.pr_src_id AS pr_src_id,
            ( EXTRACT ( EPOCH FROM pull_requests.pr_closed_at ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 3600 AS hours_to_close,
            ( EXTRACT ( EPOCH FROM pull_requests.pr_closed_at ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 86400 AS days_to_close 
        FROM
            repo,
            repo_groups,
            pull_requests 
        WHERE
            repo.repo_group_id = repo_groups.repo_group_id 
            AND repo.repo_id = pull_requests.repo_id 
            AND repo.repo_id = 26214 
            AND pull_requests.pr_src_state = 'closed' 
        ORDER BY
            hours_to_close 
        ) L 
    GROUP BY
        L.repo_id,
        L.repo_name,
        L.repo_group,
        YEAR,
        week 
    ORDER BY
        repo_id,
        YEAR,
        week 
    ) T USING ( week, YEAR ) 
ORDER BY
    YEAR,
    week;
    
SELECT
    * 
FROM
    (
    SELECT
        date_part( 'year', week :: DATE ) AS YEAR,
        date_part( 'week', week :: DATE ) AS week 
    FROM
        ( SELECT * FROM ( SELECT week :: DATE FROM generate_series ( TIMESTAMP '2013-01-01', TIMESTAMP '2020-01-30', INTERVAL '1 week' ) week ) d ) x 
    ) y
    LEFT OUTER JOIN (
    SELECT
        repo_id,
        repo_name,
        repo_group,
        date_part( 'year', pr_created_at :: DATE ) AS YEAR,
        date_part( 'week', pr_created_at :: DATE ) AS week,
        AVG ( hours_to_close ) AS wk_avg_hours_to_close,
        AVG ( days_to_close ) AS wk_avg_days_to_close,
        COUNT ( pr_src_id ) AS total_prs_open_closed 
    FROM
        (
        SELECT
            repo.repo_id AS repo_id,
            repo.repo_name AS repo_name,
            repo_groups.rg_name AS repo_group,
            pull_requests.pr_created_at AS pr_created_at,
            pull_requests.pr_closed_at AS pr_closed_at,
            pull_requests.pr_src_id AS pr_src_id,
            ( EXTRACT ( EPOCH FROM pull_requests.pr_closed_at ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 3600 AS hours_to_close,
            ( EXTRACT ( EPOCH FROM pull_requests.pr_closed_at ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 86400 AS days_to_close 
        FROM
            repo,
            repo_groups,
            pull_requests 
        WHERE
            repo.repo_group_id = repo_groups.repo_group_id 
            AND repo.repo_id = pull_requests.repo_id 
            AND repo.repo_id = 26219 
            AND pull_requests.pr_src_state = 'closed' 
        ORDER BY
            hours_to_close 
        ) L 
    GROUP BY
        L.repo_id,
        L.repo_name,
        L.repo_group,
        YEAR,
        week 
    ORDER BY
        repo_id,
        YEAR,
        week 
    ) T USING ( week, YEAR ) 
ORDER BY
    YEAR,
    week;
    
SELECT
    * 
FROM
    (
    SELECT
        date_part( 'year', week :: DATE ) AS YEAR,
        date_part( 'week', week :: DATE ) AS week 
    FROM
        ( SELECT * FROM ( SELECT week :: DATE FROM generate_series ( TIMESTAMP '2013-01-01', TIMESTAMP '2020-01-30', INTERVAL '1 week' ) week ) d ) x 
    ) y
    LEFT OUTER JOIN (
    SELECT
        repo_id,
        repo_name,
        repo_group,
        date_part( 'year', pr_created_at :: DATE ) AS YEAR,
        date_part( 'week', pr_created_at :: DATE ) AS week,
        AVG ( hours_to_close ) AS wk_avg_hours_to_close,
        AVG ( days_to_close ) AS wk_avg_days_to_close,
        COUNT ( pr_src_id ) AS total_prs_open_closed 
    FROM
        (
        SELECT
            repo.repo_id AS repo_id,
            repo.repo_name AS repo_name,
            repo_groups.rg_name AS repo_group,
            pull_requests.pr_created_at AS pr_created_at,
            pull_requests.pr_closed_at AS pr_closed_at,
            pull_requests.pr_src_id AS pr_src_id,
            ( EXTRACT ( EPOCH FROM pull_requests.pr_closed_at ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 3600 AS hours_to_close,
            ( EXTRACT ( EPOCH FROM pull_requests.pr_closed_at ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 86400 AS days_to_close 
        FROM
            repo,
            repo_groups,
            pull_requests 
        WHERE
            repo.repo_group_id = repo_groups.repo_group_id 
            AND repo.repo_id = pull_requests.repo_id 
            AND repo.repo_id = 25158 
            AND pull_requests.pr_src_state = 'closed' 
        ORDER BY
            hours_to_close 
        ) L 
    GROUP BY
        L.repo_id,
        L.repo_name,
        L.repo_group,
        YEAR,
        week 
    ORDER BY
        repo_id,
        YEAR,
        week 
    ) T USING ( week, YEAR ) 
ORDER BY
    YEAR,
    week;
    
SELECT
    * 
FROM
    (
    SELECT
        date_part( 'year', week :: DATE ) AS YEAR,
        date_part( 'week', week :: DATE ) AS week 
    FROM
        ( SELECT * FROM ( SELECT week :: DATE FROM generate_series ( TIMESTAMP '2013-01-01', TIMESTAMP '2020-01-30', INTERVAL '1 week' ) week ) d ) x 
    ) y
    LEFT OUTER JOIN (
    SELECT
        repo_id,
        repo_name,
        repo_group,
        date_part( 'year', pr_created_at :: DATE ) AS YEAR,
        date_part( 'week', pr_created_at :: DATE ) AS week,
        AVG ( hours_to_close ) AS wk_avg_hours_to_close,
        AVG ( days_to_close ) AS wk_avg_days_to_close,
        COUNT ( pr_src_id ) AS total_prs_open_closed 
    FROM
        (
        SELECT
            repo.repo_id AS repo_id,
            repo.repo_name AS repo_name,
            repo_groups.rg_name AS repo_group,
            pull_requests.pr_created_at AS pr_created_at,
            pull_requests.pr_closed_at AS pr_closed_at,
            pull_requests.pr_src_id AS pr_src_id,
            ( EXTRACT ( EPOCH FROM pull_requests.pr_closed_at ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 3600 AS hours_to_close,
            ( EXTRACT ( EPOCH FROM pull_requests.pr_closed_at ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 86400 AS days_to_close 
        FROM
            repo,
            repo_groups,
            pull_requests 
        WHERE
            repo.repo_group_id = repo_groups.repo_group_id 
            AND repo.repo_id = pull_requests.repo_id 
            AND repo.repo_id = 26217 
            AND pull_requests.pr_src_state = 'closed' 
        ORDER BY
            hours_to_close 
        ) L 
    GROUP BY
        L.repo_id,
        L.repo_name,
        L.repo_group,
        YEAR,
        week 
    ORDER BY
        repo_id,
        YEAR,
        week 
    ) T USING ( week, YEAR ) 
ORDER BY
    YEAR,
    week;
    
SELECT
    * 
FROM
    (
    SELECT
        date_part( 'year', week :: DATE ) AS YEAR,
        date_part( 'week', week :: DATE ) AS week 
    FROM
        ( SELECT * FROM ( SELECT week :: DATE FROM generate_series ( TIMESTAMP '2013-01-01', TIMESTAMP '2020-01-30', INTERVAL '1 week' ) week ) d ) x 
    ) y
    LEFT OUTER JOIN (
    SELECT
        repo_id,
        repo_name,
        repo_group,
        date_part( 'year', pr_created_at :: DATE ) AS YEAR,
        date_part( 'week', pr_created_at :: DATE ) AS week,
        AVG ( hours_to_close ) AS wk_avg_hours_to_close,
        AVG ( days_to_close ) AS wk_avg_days_to_close,
        COUNT ( pr_src_id ) AS total_prs_open_closed 
    FROM
        (
        SELECT
            repo.repo_id AS repo_id,
            repo.repo_name AS repo_name,
            repo_groups.rg_name AS repo_group,
            pull_requests.pr_created_at AS pr_created_at,
            pull_requests.pr_closed_at AS pr_closed_at,
            pull_requests.pr_src_id AS pr_src_id,
            ( EXTRACT ( EPOCH FROM pull_requests.pr_closed_at ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 3600 AS hours_to_close,
            ( EXTRACT ( EPOCH FROM pull_requests.pr_closed_at ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 86400 AS days_to_close 
        FROM
            repo,
            repo_groups,
            pull_requests 
        WHERE
            repo.repo_group_id = repo_groups.repo_group_id 
            AND repo.repo_id = pull_requests.repo_id 
            AND repo.repo_id = 26218 
            AND pull_requests.pr_src_state = 'closed' 
        ORDER BY
            hours_to_close 
        ) L 
    GROUP BY
        L.repo_id,  
        L.repo_name,
        L.repo_group,
        YEAR,
        week 
    ORDER BY
        repo_id,
        YEAR,
        week 
    ) T USING ( week, YEAR ) 
ORDER BY
    YEAR,
    week;

```

## Comments on Issues Overall
```sql

/**
RIOT: 26214
NUTTX: 26219
Zephyr: 25158
Amazon-FreeRTOS: 26217
mbed OS: 26218
**/

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
        COUNT ( k.issue_msg_ref_id ) AS comment_count 
    FROM
        issues
        LEFT OUTER JOIN issue_message_ref K ON issues.issue_id = K.issue_id 
        WHERE
        pull_request IS NULL 
    GROUP BY
        issues.issue_id,
        issues.repo_id 
    ORDER BY
        issues.repo_id 
    ) D ON repo.repo_id = D.repo_id, 
        repo_groups, 
        (select repo.repo_id, count(issues.issue_id) as issues_count from repo left outer join issues on issues.repo_id = repo.repo_id group by repo.repo_id) E
where repo.repo_group_id = repo_groups.repo_group_id and repo.repo_id = E.repo_id 
and repo.repo_id in (26214, 26219, 25158, 26217, 26218)
GROUP BY
    repo.repo_id,
    repo.repo_name, 
        repo_groups.rg_name,
                E.issues_count
ORDER BY
    rg_name, repo_name;
        
```
