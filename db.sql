CREATE DATABASE core;
USE core;

CREATE TABLE `position` (
    txid VARCHAR(48) NOT NULL,
    closing_txid VARCHAR(48) NOT NULL,
    `type` VARCHAR(8),
    closed_at DATETIME,
    primary key (txid)
);

CREATE TABLE `order` (
    txid VARCHAR(48) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    pair VARCHAR(8),
    `type` VARCHAR(8),
    volume FLOAT(8),
    price  FLOAT(8),
    cost FLOAT(8),
    time_frame INT,
    status VARCHAR(8),
    closed_at DATETIME,
    primary key (txid)
);

CREATE TABLE `trade` (
    txid VARCHAR(48) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    pair VARCHAR(32),
    cost FLOAT(8),
    fee FLOAT(8),
    price FLOAT(8),
    closed_at DATETIME,
    primary key (txid)
);

CREATE TABLE `settings` (
    id BIGINT(8) AUTO_INCREMENT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    setting VARCHAR(32),
    enabled BIT,
    primary key (id)
);

INSERT INTO `settings` (setting, enabled) VALUES ('trading_enabled', 0);
INSERT INTO `settings` (setting, enabled) VALUES ('created_at', 1);