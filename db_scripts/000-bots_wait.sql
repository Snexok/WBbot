create table bots_wait
(
	id serial not null
		constraint bots_waits_pk
			primary key,
	bot_name text,
	event text,
	start_datetime timestamp,
	end_datetime timestamp
);

alter table bots_wait owner to postgres;

