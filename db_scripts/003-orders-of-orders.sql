create table orders_of_orders
(
    id                   text not null
        constraint orders_of_orders_pk
            primary key,
    inn                  text,
    articles             text[],
    active               integer[],
    quantities_to_bought integer[],
    quantities_bought    integer[],
    search_keys          text[],
    numbers_of_comments  integer[],
    comments             text[][],
    unused_comments      text[][],
    left_comments        text[][],
    bought_per_day       integer,
    budget               integer,
    remaining_budget     integer,
    start_datetime       timestamp,
    end_datetime         timestamp
);

alter table orders_of_orders
    owner to postgres;

