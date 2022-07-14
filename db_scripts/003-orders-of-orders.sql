create table orders_of_orders
(
    id                   integer not null
        constraint orders_of_orders_pk
            primary key,
    inn                  text,
    articles             text[],
    quantities_to_bought integer[],
    quantities_bought    integer[],
    search_keys          text[],
    numbers_of_comments  integer[],
    comments             text[],
    bought_per_day       integer,
    budget               integer,
    remaining_budget     integer,
    start_datetime       timestamp,
    end_datetime         timestamp
);

alter table orders_of_orders
    owner to postgres;

