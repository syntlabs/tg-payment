-- Enums
DO $$ BEGIN
    CREATE TYPE transaction_types AS ENUM (
        'became_referral',
        'referral_profit',
        'balance_replenishment',
        'subscription_purchase'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Таблицы
CREATE TABLE IF NOT EXISTS users (
    telegram_id BIGSERIAL PRIMARY KEY,
    balance DOUBLE PRECISION NOT NULL DEFAULT 0.00,
    referrer_uuid VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS referrals (
    referrer_id BIGSERIAL NOT NULL,
    referral_id BIGSERIAL NOT NULL UNIQUE,

    FOREIGN KEY (referrer_id) REFERENCES users (telegram_id),
    FOREIGN KEY (referral_id) REFERENCES users (telegram_id)
);

CREATE TABLE IF NOT EXISTS subscription_notifications (
    user_id BIGINT UNIQUE NOT NULL,
    enable_notifications BOOLEAN NOT NULL DEFAULT true,
    date_of_notification TIMESTAMP NULL,
    notified BOOLEAN NOT NULL DEFAULT true,

    FOREIGN KEY (user_id) REFERENCES users (telegram_id)
);

CREATE TABLE IF NOT EXISTS transactions (
    user_id BIGSERIAL NOT NULL,
    balance_change DOUBLE PRECISION NOT NULL,
    date_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    transaction_type transaction_types NOT NULL,

    FOREIGN KEY (user_id) REFERENCES users (telegram_id)
);

CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id BIGSERIAL PRIMARY KEY,
    owner_id BIGSERIAL UNIQUE NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    expires_on TIMESTAMP NOT NULL,

    FOREIGN KEY (owner_id) REFERENCES users (telegram_id)
);

CREATE TABLE IF NOT EXISTS devices (
    subscription_id BIGSERIAL NOT NULL,
    device_uuid VARCHAR(100) UNIQUE NOT NULL,
    last_used TIMESTAMP NOT NULL,

    FOREIGN KEY (subscription_id) REFERENCES subscriptions (subscription_id)
);


-- Функции, триггеры и пр.

-- Добавление реферального бонуса
CREATE OR REPLACE FUNCTION add_referral_bonus()
RETURNS TRIGGER AS $$
BEGIN
    -- Записываем транзакцию в таблицу transactions
    INSERT INTO transactions (user_id, balance_change, transaction_type)
    VALUES (NEW.referral_id, 50, 'became_referral');
    -- Благодаря триггеру after_transaction_insert баланс у реферала уже пополнится

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER after_referral_insert
AFTER INSERT ON referrals
FOR EACH ROW
EXECUTE FUNCTION add_referral_bonus();

-- Обновление баланса пользователя в соответствие с транзакциями
CREATE OR REPLACE FUNCTION update_user_balance()
RETURNS TRIGGER AS $$
BEGIN
    -- Увеличиваем баланс пользователя на значение balance_change
    UPDATE users
    SET balance = balance + NEW.balance_change
    WHERE telegram_id = NEW.user_id;

    -- Проверяем, не стал ли баланс отрицательным
    IF (SELECT balance FROM users WHERE telegram_id = NEW.user_id) < 0 THEN
        RAISE EXCEPTION 'User balance cannot be negative';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER after_transaction_insert
AFTER INSERT ON transactions
FOR EACH ROW
EXECUTE FUNCTION update_user_balance();

-- Добавление записи в subscription_notifications после добавления пользователя
CREATE OR REPLACE FUNCTION add_subscription_notifications()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO subscription_notifications (user_id)
    VALUES (NEW.telegram_id);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER after_user_insert
AFTER INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION add_subscription_notifications();

-- Обновление даты уведомления пользователя
CREATE OR REPLACE FUNCTION update_subscription_notifications()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE subscription_notifications
    SET date_of_notification = NEW.expires_on - INTERVAL '3 days', notified = FALSE
    WHERE user_id = NEW.owner_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER subscription_notifications_trigger
AFTER INSERT OR UPDATE ON subscriptions
FOR EACH ROW
EXECUTE FUNCTION update_subscription_notifications();

-- Удаление неиспользуемых устройств
CREATE OR REPLACE FUNCTION delete_old_devices()
RETURNS VOID AS $$
BEGIN
    DELETE FROM devices
    WHERE last_used < NOW() - INTERVAL '14 days';
END;
$$ LANGUAGE plpgsql;

-- Распределение пополненной суммы среди рефереров
CREATE OR REPLACE FUNCTION distribute_referral_bonus()
RETURNS TRIGGER AS $$
DECLARE
    next_referrer_id BIGINT;
    referral_bonus DOUBLE PRECISION;
BEGIN
    referral_bonus := NEW.balance_change * 0.15;

    -- Получаем ID реферера 1-го уровня
    SELECT referrer_id INTO next_referrer_id
    FROM referrals
    WHERE referral_id = NEW.user_id;

    -- Цикл для распределения бонуса среди рефереров
    WHILE next_referrer_id IS NOT NULL LOOP
        -- Заносим транзакцию + обновляем баланс реферера (через треггер)
        INSERT INTO transactions (user_id, balance_change, transaction_type)
        VALUES (next_referrer_id, referral_bonus, 'referral_profit');

        -- Переходим к следующему рефереру
        SELECT referrer_id INTO next_referrer_id
        FROM referrals
        WHERE referral_id = next_referrer_id;

        referral_bonus := referral_bonus * 0.15;
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER after_balance_replenishment
AFTER INSERT ON transactions
FOR EACH ROW
WHEN (NEW.transaction_type = 'balance_replenishment')
EXECUTE FUNCTION distribute_referral_bonus();