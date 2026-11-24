-- Jeu de démonstration : un fonds, deux jours de cotation (mêmes chiffres que les tests).
insert into fund (id, name) values ('FL-0001', 'FundLens Actions Europe');

insert into snapshot (fund_id, as_of, shares_outstanding, cash) values
    ('FL-0001', date '2026-11-20', 125000, 48250.75),
    ('FL-0001', date '2026-11-23', 125000, 48250.75);

insert into snapshot_position (snapshot_id, isin, quantity)
select s.id, p.isin, p.quantity
from snapshot as s
cross join (values ('FR0000120271', 12000), ('FR0000131104', 8500), ('US0378331005', 1500)) as p (isin, quantity);

insert into price (isin, as_of, currency, close) values
    ('FR0000120271', date '2026-11-20', 'EUR', 61.42),
    ('FR0000131104', date '2026-11-20', 'EUR', 74.18),
    ('US0378331005', date '2026-11-20', 'USD', 228.35),
    ('FR0000120271', date '2026-11-23', 'EUR', 63.00),
    ('FR0000131104', date '2026-11-23', 'EUR', 72.50),
    ('US0378331005', date '2026-11-23', 'USD', 230.00);

insert into fx_rate (currency, as_of, rate_to_eur) values
    ('USD', date '2026-11-20', 0.92),
    ('USD', date '2026-11-23', 0.92);
