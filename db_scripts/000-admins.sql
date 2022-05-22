create table admins
(
	id text not null
		constraint admins_pk
			primary key,
	name text,
	sentry boolean
);

alter table admins owner to postgres;

create unique index admins_id_uindex
	on admins (id);

