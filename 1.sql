--
-- Файл сгенерирован с помощью SQLiteStudio v3.3.2 в Сб окт 16 12:43:44 2021
--
-- Использованная кодировка текста: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Таблица: settings
DROP TABLE IF EXISTS settings;

CREATE TABLE settings (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    token VARCHAR
);

INSERT INTO settings (id, token) VALUES (0, '1686468227:AAHJW9ZAbkjSzvOyoZHXEUigGG2NU4mQiDU');

-- Таблица: subscriptions
DROP TABLE IF EXISTS subscriptions;

CREATE TABLE subscriptions (
    id         INTEGER PRIMARY KEY,
    user_id    VARCHAR,
    username   VARCHAR,
    password   VARCHAR,
    hasAccount BOOLEAN DEFAULT (0),
    isBusiness BOOLEAN DEFAULT (0),
    isAdmin    BOOLEAN DEFAULT (0) 
);

INSERT INTO subscriptions (id, user_id, username, password, hasAccount, isBusiness, isAdmin) VALUES (1, '335271283', 'Koala610', '787898', 1, 0, 1);
INSERT INTO subscriptions (id, user_id, username, password, hasAccount, isBusiness, isAdmin) VALUES (2, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO subscriptions (id, user_id, username, password, hasAccount, isBusiness, isAdmin) VALUES (3, '1222039126', NULL, NULL, 0, 0, 0);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
