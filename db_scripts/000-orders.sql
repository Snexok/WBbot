create table IF NOT EXISTS orders
(
	id integer not null
		constraint orders_pkey
			primary key,
	number integer,
	total_price integer,
	services_price integer,
	prices integer[],
	quantities integer[],
	articles text[],
	pup_address text,
	pup_tg_id text,
	bot_name text,
	bot_surname text,
	start_date date,
	pred_end_date date,
	end_date date,
	code_for_approve text,
	active boolean,
	statuses text[]
);

alter table orders owner to postgres;

