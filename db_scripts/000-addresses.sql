create table IF NOT EXISTS addresses
(
	id integer not null
		constraint addresses_pkey
			primary key,
	address text,
	tg_id text,
	added_to_bot boolean
);

alter table addresses owner to postgres;

