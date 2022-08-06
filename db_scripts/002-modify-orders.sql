alter table orders
	add inn text,
	add collected boolean,
    add commented boolean,
	add order_id text;

create unique index orders_order_id_uindex
	on orders (order_id);

