create table stock_availability
(
	id text not null
		constraint rstock_availability_pk
			primary key,
    type text,
	quantity integer
);

alter table stock_availability owner to postgres;

