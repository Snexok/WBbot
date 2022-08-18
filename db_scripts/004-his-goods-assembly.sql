create table his_goods_assembly
(
	id serial not null
		constraint his_goods_assembly_pk
			primary key,
    article text,
	package text,
	assembly_cost integer,
    packaging_cost integer,
    profit integer,
    datetime timestamp
);

alter table his_goods_assembly owner to postgres;

