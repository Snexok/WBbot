alter table delivery alter column start_date type timestamp using start_date::timestamp;

alter table delivery alter column pred_end_date type timestamp using pred_end_date::timestamp;

alter table delivery alter column end_date type timestamp using end_date::timestamp;
