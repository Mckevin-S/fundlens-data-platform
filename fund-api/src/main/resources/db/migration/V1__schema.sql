create table fund (
    id varchar(7) primary key,
    name varchar(200) not null,
    currency char(3) not null default 'EUR'
);

create table snapshot (
    id bigserial primary key,
    fund_id varchar(7) not null references fund (id),
    as_of date not null,
    shares_outstanding numeric(20, 4) not null check (shares_outstanding > 0),
    cash numeric(20, 2) not null,
    unique (fund_id, as_of)
);

create table snapshot_position (
    id bigserial primary key,
    snapshot_id bigint not null references snapshot (id) on delete cascade,
    isin char(12) not null,
    quantity numeric(20, 4) not null
);

create table price (
    isin char(12) not null,
    as_of date not null,
    currency char(3) not null,
    close numeric(20, 6) not null check (close > 0),
    primary key (isin, as_of)
);

create table fx_rate (
    currency char(3) not null,
    as_of date not null,
    rate_to_eur numeric(20, 8) not null check (rate_to_eur > 0),
    primary key (currency, as_of)
);

create table nav (
    fund_id varchar(7) not null references fund (id),
    as_of date not null,
    net_assets numeric(20, 2) not null,
    nav_per_share numeric(20, 4) not null,
    computed_at timestamptz not null default now(),
    primary key (fund_id, as_of)
);

create table nav_alert (
    id bigserial primary key,
    fund_id varchar(7) not null references fund (id),
    as_of date not null,
    variation numeric(12, 6) not null,
    message text not null,
    created_at timestamptz not null default now()
);

create table audit_log (
    id bigserial primary key,
    at timestamptz not null default now(),
    action varchar(50) not null,
    fund_id varchar(7),
    detail text
);
