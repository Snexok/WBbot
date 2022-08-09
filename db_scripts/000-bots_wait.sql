create table bots_wait
(
	id serial not null
		constraint bots_waits_pk
			primary key,
    order_id text,
	bot_name text,
	event text,
	sub_event text,
    datetime_to_run timestamp,
	wait boolean default FALSE,
	running boolean default FALSE,
    pause boolean default FALSE,
	data json,
	start_datetime timestamp,
	end_datetime timestamp
);

alter table bots_wait owner to postgres;

