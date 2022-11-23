-----------------------------------------
--- Creating sample process log table --- 
-----------------------------------------
create table processes 
( 
log_id int null,
process_id int null,
start_time datetime null,
end_time datetime null
);

-----------------------------------
------- Inserting the values ------ 
-----------------------------------
insert into processes values
(1,1,'2022-10-01 05:01:12','2022-10-01 05:06:23'),  -- 5:00 - 5:15
(2,2,'2022-10-01 05:05:12','2022-10-01 05:23:23'),  -- 5:15 - 5:30 and 5:00 - 5:15
(3,1,'2022-10-01 05:31:01','2022-10-31 05:40:32'),  -- 5:30 - 5:45 onwards all
(4,3,'2022-10-01 06:01:12','2022-10-31 08:10:01')   -- 6:00 - 6:15 onwards all
;


-----------------------------------------------------------
---- This is based on the business on a particular day ----
---- To make in based on only time we can use          ----
---- cast(p.start_time as time) and use the same       ----
-----------------------------------------------------------
DECLARE @DateToTrack AS VARCHAR(100)
SET @DateToTrack = '2022-10-01'
BEGIN
  with d as (
    select 
    cast(@DateToTrack as datetime) as time_slots_start,
    dateadd(minute, 15, cast(@DateToTrack as datetime)) as time_slots_end
    union all
    select dateadd(minute, 15, time_slots_start),dateadd(minute, 15, time_slots_end)
    from d
    where dateadd(minute, 15, time_slots_start) < dateadd(day, 1, @DateToTrack)
  ),
  tbl_process_count as (
  select 
  d.*,count(distinct p.process_id) as process_count
  --p.*
  --,count(distinct p.process_id)
  from d
  left join processes p on
  -- started before ended after
  --and 
  (  
    ( p.start_time<= d.time_slots_start and p.end_time >= d.time_slots_end)
    or
    (
      (p.start_time BETWEEN d.time_slots_start and d.time_slots_end)
      or
      (p.end_time BETWEEN d.time_slots_start and d.time_slots_end)
    )
  )
  group by d.time_slots_start,d.time_slots_end
    )
    -------------------------------
    -------- ANSWER FOR 3.a -------
    -------------------------------
    select 'most_busiest' as time_flags,* from tbl_process_count
    where process_count = (select max(process_count) from tbl_process_count)
    -------------------------------
    -------- ANSWER FOR 3.b -------
    -------------------------------
    union all
    select 'most_idle' as time_flags,* from tbl_process_count
    where process_count = 0
    option (maxrecursion 0)
END;
