CREATE TABLE "User" (
  id bigserial PRIMARY KEY,
  card_number varchar(20) UNIQUE,
  "limit" DECIMAL,
  hashed_password varchar(100),
  is_active boolean,
  _balance DECIMAL
);

--add user
INSERT INTO "User" (card_number, "limit", hashed_password, is_active, is_verified, _balance) VALUES
('100500', 100.00, 'hashed_password_1', true, false, 500.00),
('999999', 100.00, 'hashed_password_2', true, false, 500.00);

UPDATE "User" SET _balance = 0 where card_number = '100500';

SELECT * FROM "User";

--get_user
SELECT * FROM "User" where card_number = '100500';

--get_balance
SELECT card_number, _balance FROM "User" where card_number = '100500';

--deposit
UPDATE "User" SET _balance = _balance + 1000 where card_number = '100500';

--withdrawal
UPDATE "User" SET _balance = _balance - 1000 where card_number = '100500';

--change_limit
UPDATE "User" SET "limit" = 1000 where card_number = '100500';

DELETE FROM "User" where id = 2;
