CREATE TABLE IF NOT EXISTS users (
    telegram_id BIGSERIAL PRIMARY KEY,
    balance DOUBLE PRECISION NOT NULL DEFAULT 0.00,
    enable_notifications BOOLEAN NOT NULL DEFAULT false,
    referrer_uuid VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS referrals (
    referrer_id BIGSERIAL NOT NULL,
    referral_id BIGSERIAL NOT NULL UNIQUE,

    FOREIGN KEY (referrer_id) REFERENCES users (telegram_id),
    FOREIGN KEY (referral_id) REFERENCES users (telegram_id)
);

CREATE TABLE IF NOT EXISTS transactions (
    user_id BIGSERIAL NOT NULL,
    balance_change DOUBLE PRECISION NOT NULL,
    date_time TIMESTAMP NOT NULL,
    comment TEXT NULL,

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
    device_uuid VARCHAR(100) NOT NULL,
    last_used TIMESTAMP NOT NULL,

    FOREIGN KEY (subscription_id) REFERENCES subscriptions (subscription_id)
);