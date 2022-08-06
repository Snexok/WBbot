create table IF NOT EXISTS bots
(
	id integer default 0,
	name text,
	addresses text[],
	number text,
	username text
);

alter table bots owner to postgres;

