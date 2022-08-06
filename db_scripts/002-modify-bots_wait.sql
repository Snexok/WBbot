alter table bots_wait
	add wait boolean default FALSE,
	add data json,
    add order_id text,
    add pause bool default FALSE,
    add datetime_to_run timestamp;

