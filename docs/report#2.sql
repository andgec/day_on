    
SELECT
    usr.username,
  	object_id,
    employee_id,
    total_working_time,
    work_date
FROM
    (SELECT
      content_type_id,
      object_id,
      employee_id,
      work_date,
      sum(work_time) as total_time
    FROM
      receivables_worktimejournal
    WHERE
      object_id = 1
    GROUP BY
      content_type_id,
      object_id,
      employee_id,
      work_date
    ) AS ts
    RIGHT OUTER JOIN djauth_user usr on usr.id = ts.employee_id
ORDER BY
  ts.content_type_id,
  ts.object_id,
  ts.employee_id,
  ts.work_date
