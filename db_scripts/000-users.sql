create table IF NOT EXISTS users
(
	id text not null
		constraint users_pkey
			primary key,
	pup_state integer,
	name text,
	addresses text[],
	username text
);

alter table users owner to postgres;

