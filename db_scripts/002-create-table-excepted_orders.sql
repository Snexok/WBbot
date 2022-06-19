create table IF NOT EXISTS excepted_orders
(
	id int not null
		constraint excepted_orders_pkey
			primary key,
	inn text,
	order_number text,
	start_datetime timestamp
)
