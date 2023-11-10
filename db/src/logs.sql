CREATE TABLE CommonLog (
  id bigserial PRIMARY KEY,
  card_number varchar(20),
  before varchar(300),
  after varchar(300),
  changes varchar(300),
  user_id bigint REFERENCES "User" (id) ON DELETE CASCADE,
  _datetime_utc timestamp
);


INSERT INTO CommonLog (card_number, before, after, changes, user_id, _datetime_utc)
VALUES
  ('100500', 'Before value 1', 'After value 1', 'Changes 1', 1, '2023-09-29 04:31:13');


CREATE TABLE BalanceLog (
  id bigserial PRIMARY KEY,
  card_number varchar(20),
  before DECIMAL,
  after DECIMAL,
  changes DECIMAL,
  user_id bigint REFERENCES "User" (id) ON DELETE CASCADE,
  _datetime_utc timestamp
);


INSERT INTO BalanceLog (card_number, before, after, changes, user_id, _datetime_utc)
VALUES
  ('100500', 1000.00, 0.00, -1000.00, 1, '2023-09-29 04:31:13'),
  ('100500', 500.00, 1000.00, 500.00, 1, '2023-09-27 04:31:13'),
  ('100500', 0.00, 500.00, 300.00, 1, '2023-09-20 04:31:13');


SELECT * FROM CommonLog;
SELECT * FROM BalanceLog;


UPDATE BalanceLog SET changes = 500 where _datetime_utc = '2023-09-20 04:31:13';
UPDATE CommonLog SET before = 'Before value 2' where _datetime_utc = '2023-09-29 04:31:13';

--get_balance_history
SELECT *
FROM BalanceLog
WHERE user_id = 1
  AND _datetime_utc >= '2023-09-21 04:31:13'
  AND _datetime_utc <= '2023-09-29 04:31:13';


DELETE FROM BalanceLog where _datetime_utc = '2023-09-20 04:31:13';
DELETE FROM CommonLog where _datetime_utc = '2023-09-29 04:31:13';