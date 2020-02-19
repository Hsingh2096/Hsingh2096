# Issues 

## Average Comments

### To Do

### SQL for Comments on Average, with Standard Deviation
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

### SQL for Comments Over Time
```sql
/**
RIOT: 26214
NUTTX: 26219
Zephyr: 25158
Amazon-FreeRTOS: 26217
mbed OS: 26218


unfinished .
**/

SELECT
    repo.repo_id,
    repo.repo_name,
        repo_groups.rg_name,
                E.issues_count,

FROM
    repo
    LEFT OUTER JOIN (
    SELECT
        issues.issue_id,
        issues.repo_id,
        EXTRACT ( EPOCH FROM event_created_at )) - EXTRACT ( EPOCH FROM issue_created_at )) / 3600 AS hours_to_first_close,
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

### Working Notes
```sql
   select C.repo_id, avg(comment_count) as average_comments, max(comment_count) as max_comments, min(comment_count) as min_comments, stddev(comment_count)as stddev_comments  from 
     (
     SELECT issues.issue_id, issues.repo_id,
                    count(*) as comment_count
                FROM issues
                                LEFT OUTER JOIN issue_message_ref k on issues.issue_id = k.issue_id
                WHERE -- issues.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = 1)
                pull_request is NULL
                GROUP BY issues.issue_id, issues.repo_id
                                ORDER BY issues.repo_id 
                                
) C LEFT OUTER JOIN repo j on C.repo_id=j.repo_id 
group by C.repo_id
order by average_comments desc; 

select repo.repo_id, repo.repo_name, count(*) as issues_count from repo 
left outer join issues a on repo.repo_id=a.repo_id
group by repo.repo_id, repo.repo_name
order by issues_count; 

select count(*) from repo; 
select repo_id, count(*) from issues group by repo_id; 

-- another set 

   select C.repo_id, avg(comment_count) as average_comments, max(comment_count) as max_comments, min(comment_count) as min_comments, stddev(comment_count)as stddev_comments  from 
     (
     SELECT issues.issue_id, issues.repo_id,
                    count(*) as comment_count
                FROM issues
                                LEFT OUTER JOIN issue_message_ref k on issues.issue_id = k.issue_id
                WHERE -- issues.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = 1)
                pull_request is NULL
                GROUP BY issues.issue_id, issues.repo_id
                                ORDER BY issues.repo_id 
                                
) C LEFT OUTER JOIN repo j on C.repo_id=j.repo_id 
group by C.repo_id
order by average_comments desc; 

select repo.repo_id, repo.repo_name, sum(D.comment_count) from repo 
left outer join (
     SELECT issues.issue_id, issues.repo_id,
                    count(*)-1 as comment_count
                FROM issues
                                LEFT OUTER JOIN issue_message_ref k on issues.issue_id = k.issue_id
                WHERE -- issues.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = 1)
                pull_request is NULL
                GROUP BY issues.issue_id, issues.repo_id
                                ORDER BY issues.repo_id) D on repo.repo_id=D.repo_id
                                group by repo.repo_id, repo.repo_name 
                                order by comment_count; 
                                
select issues.issue_id, count(*)-1 as counter from issues left outer join issue_message_ref j on issues.issue_id = j.issue_id group by issues.issue_id order by counter;

select sum(counter) from (select issues.issue_id, count(*)-1 as counter from issues left outer join issue_message_ref j on issues.issue_id = j.issue_id group by issues.issue_id order by counter) x; 

select count(*) from issues; 

select count(*) from issue_message_ref; 


select * from issue_message_ref where issue_id = 152916; 
                                
select repo.repo_id, repo.repo_name, a.comment_count, count(*) from repo 
left outer join (
    SELECT issues.issue_id, issues.repo_id,
                    count(*) as comment_count
                FROM issues
                                LEFT OUTER JOIN issue_message_ref k on issues.issue_id = k.issue_id
                WHERE -- issues.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = 1)
                pull_request is NULL
                GROUP BY issues.issue_id, issues.repo_id
                                ORDER BY issues.repo_id 
)
a on repo.repo_id=a.repo_id
group by repo.repo_id, repo.repo_name, a.comment_count;


select count(*) from repo; 
select repo_id, count(*) from issues group by repo_id; 

select repo.repo_id, repo.repo_name, avg(D.comment_count) as average_comments, max(D.comment_count) as max_comments, min(D.comment_count) as min_comments, stddev(D.comment_count)as stddev_comments from repo 
left outer join (
     SELECT issues.issue_id, issues.repo_id,
                    count(*)-1 as comment_count
                FROM issues
                                LEFT OUTER JOIN issue_message_ref k on issues.issue_id = k.issue_id
                WHERE -- issues.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = 1)
                pull_request is NULL
                GROUP BY issues.issue_id, issues.repo_id
                                ORDER BY issues.repo_id) D on repo.repo_id=D.repo_id
                                group by repo.repo_id, repo.repo_name
                                order by repo_name;

--- working notes 

select C.repo_id, avg(comment_count) as average_comments, max(comment_count) as max_comments, min(comment_count) as min_comments, stddev(comment_count)as stddev_comments  from 
     (
     SELECT issues.issue_id, issues.repo_id,
                    count(*) as comment_count
                FROM issues
                                LEFT OUTER JOIN issue_message_ref k on issues.issue_id = k.issue_id
                WHERE -- issues.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = 1)
                pull_request is NULL
                GROUP BY issues.issue_id, issues.repo_id
                                ORDER BY issues.repo_id 
                                
) C LEFT OUTER JOIN repo j on C.repo_id=j.repo_id 
group by C.repo_id
order by average_comments desc;
                                
select count(*) from repo; 
                                
select issues.issue_id, count(*)-1 as counter from issues left outer join issue_message_ref j on issues.issue_id = j.issue_id group by issues.issue_id order by counter;

select sum(counter) from (select issues.issue_id, count(*)-1 as counter from issues left outer join issue_message_ref j on issues.issue_id = j.issue_id group by issues.issue_id order by counter) x; 

select count(*) from issues; 

select repo.repo_id, repo.repo_name, avg(D.comment_count) as average_comments, max(D.comment_count) as max_comments, min(D.comment_count) as min_comments, stddev(D.comment_count)as stddev_comments from repo 
left outer join (
     SELECT issues.issue_id, issues.repo_id,
                    count(*)-1 as comment_count
                FROM issues
                                LEFT OUTER JOIN issue_message_ref k on issues.issue_id = k.issue_id
                WHERE -- issues.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = 1)
                pull_request is NULL
                GROUP BY issues.issue_id, issues.repo_id
                                ORDER BY issues.repo_id) D on repo.repo_id=D.repo_id
                                group by repo.repo_id, repo.repo_name
                                order by repo_name;

select count(*) from issue_message_ref; 


select * from issue_message_ref where issue_id = 152916; 
                                
select repo.repo_id, repo.repo_name, a.comment_count, count(*) from repo 
left outer join (
    SELECT issues.issue_id, issues.repo_id,
                    count(*) as comment_count
                FROM issues
                                LEFT OUTER JOIN issue_message_ref k on issues.issue_id = k.issue_id
                WHERE -- issues.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = 1)
                pull_request is NULL
                GROUP BY issues.issue_id, issues.repo_id
                                ORDER BY issues.repo_id 
)
a on repo.repo_id=a.repo_id
group by repo.repo_id, repo.repo_name, a.comment_count;


select count(*) from repo; 
select repo_id, count(*) from issues group by repo_id; 

```
