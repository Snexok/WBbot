create table ref_stock_goods
(
	id serial not null
		constraint ref_stock_goods_pk
			primary key,
    article text,
    barcode text,
	package text,
	assembly_cost integer,
    packaging_cost integer,
    profit integer
);

alter table ref_stock_goods owner to postgres;

