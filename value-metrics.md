## Value Worker Labor Summaries
```sql 
select * from repo_labor where repo_id = 2119; 

select repo_id, programming_language, sum(total_lines) as repo_total_lines, sum(code_lines) as repo_code_lines, sum(comment_lines) as repo_comment_lines, sum(blank_lines) as repo_blank_lines, avg(code_complexity) as repo_lang_avg_code_complexity
from repo_labor where repo_id = 2119 group by repo_id, programming_language;


```


## Labor Cost by project and programming language
```sql
select c.repo_id, c.repo_name, sum(estimated_labor_hours)
from
(
select a.repo_id, b.repo_name, programming_language, sum(total_lines) as repo_total_lines, sum(code_lines) as repo_code_lines, sum(comment_lines) as repo_comment_lines, 
sum(blank_lines) as repo_blank_lines, avg(code_complexity) as repo_lang_avg_code_complexity, 
avg(code_complexity)*sum(code_lines)+20 as estimated_labor_hours
from repo_labor a, repo b 
where a.repo_id = b.repo_id
group by a.repo_id, programming_language, repo_name
order by repo_name, a.repo_id, programming_language
) c
group by repo_id, repo_name; 


select c.repo_id, c.repo_name, programming_language, sum(estimated_labor_hours)
from
(
select a.repo_id, b.repo_name, programming_language, sum(total_lines) as repo_total_lines, sum(code_lines) as repo_code_lines, sum(comment_lines) as repo_comment_lines, 
sum(blank_lines) as repo_blank_lines, avg(code_complexity) as repo_lang_avg_code_complexity, 
avg(code_complexity)*sum(code_lines)+20 as estimated_labor_hours
from repo_labor a, repo b 
where a.repo_id = b.repo_id
group by a.repo_id, programming_language, repo_name
order by repo_name, a.repo_id, programming_language
) c
where repo_id = 22249
group by repo_id, repo_name, programming_language
order by programming_language;
```




