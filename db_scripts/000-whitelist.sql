create table IF NOT EXISTS whitelist
(
	id integer not null
		constraint whitelist_pk
			primary key,
	tg_id text,
	username text,
	secret_key text
);

alter table whitelist owner to postgres;

