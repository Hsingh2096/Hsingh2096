## SPDX Queries

```sql
select the_license_id as license_id, short_name, sum(count) as count from 
(SELECT A
	.license_id as the_license_id,
	b.short_name as short_name,
	COUNT ( * ) 
FROM
	files_licenses A,
	licenses b,
	augur_repo_map C,
	packages d,
	files e 
WHERE
	A.license_id = b.license_id 
	AND d.package_id = C.dosocs_pkg_id 
	AND e.file_id = A.file_id 
	AND e.package_id = d.package_id 
	AND C.repo_id = 25158 
	AND b.is_spdx_official = 't'
GROUP BY
	the_license_id,
	b.short_name 
UNION
SELECT 
	500 as the_license_id,
	'No Warranty' as short_name,
	COUNT ( * ) 
FROM
	files_licenses A,
	licenses b,
	augur_repo_map C,
	packages d,
	files e 
WHERE
	A.license_id = b.license_id 
	AND d.package_id = C.dosocs_pkg_id 
	AND e.file_id = A.file_id 
	AND e.package_id = d.package_id 
	AND C.repo_id = 25158 
	AND b.is_spdx_official = 'f'
GROUP BY
	the_license_id,
	short_name) L
GROUP BY 
	the_license_id, 
	short_name 
ORDER BY 
	short_name; 


    select a.license_id, b.short_name, count(*) from files_licenses a, licenses b, augur_repo_map c, packages d, files e
    where a.license_id = b.license_id
    and
    d.package_id = c.dosocs_pkg_id
    and
    e.file_id = a.file_id
    and
    e.package_id = d.package_id
    and
    c.repo_id = :repo_id
    group by a.license_id, b.short_name
    order by b.short_name;
```


```sql

SELECT A
    .license_id as the_license_id,
    b.short_name as short_name,
    f.file_name 
FROM
    files_licenses A,
    licenses b,
    augur_repo_map C,
    packages d,
    files e, 
    packages_files f
WHERE
    A.license_id = b.license_id 
    AND d.package_id = C.dosocs_pkg_id 
    AND e.file_id = A.file_id 
    AND e.package_id = d.package_id 
    AND C.repo_id = 25158 
    AND e.file_id = f.file_id
    AND b.license_id = 21

```


```sql
SELECT A
    .license_id as the_license_id,
    b.short_name as short_name,
    f.file_name 
FROM
    files_licenses A,
    licenses b,
    augur_repo_map C,
    packages d,
    files e, 
    packages_files f
WHERE
    A.license_id = b.license_id 
    AND d.package_id = C.dosocs_pkg_id 
    AND e.file_id = A.file_id 
    AND e.package_id = d.package_id 
    AND C.repo_id = 25158 
    AND e.file_id = f.file_id
    AND b.is_spdx_official = 't'
    AND b.license_id = 21
    

```