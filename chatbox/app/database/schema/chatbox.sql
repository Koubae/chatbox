PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS `user` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `username` TEXT NOT NULL UNIQUE,
    `password` TEXT NOT NULL,

    `created` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `modified` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS `user_username_index` ON `user` (`username`);


CREATE TABLE IF NOT EXISTS `server_session` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `session_id` INTEGER NOT NULL UNIQUE,
    `data` BLOB,

    `created` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `modified` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS `server_session_session_id_index` ON `server_session` (`session_id`);


CREATE TABLE IF NOT EXISTS `user_login` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `user_id` INTEGER NOT NULL,
    `session_id` INTEGER NOT NULL,
    `attempts` INTEGER NOT NULL,

    `created` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `modified` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE ,
    FOREIGN KEY ('session_id') REFERENCES `server_session`(`id`) ON DELETE CASCADE

);


CREATE TABLE IF NOT EXISTS `message` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `session_id` INTEGER NOT NULL,

    `owner_name` TEXT NOT NULL,
    `from_name` TEXT NOT NULL,
    `from_role` TEXT NOT NULL,
    `to_name` TEXT NOT NULL,
    `to_role` TEXT NOT NULL,

    `body` TEXT NOT NULL,
    'owner' BLOB NOT NULL,
    'sender' BLOB NOT NULL,
    'to' BLOB NOT NULL,

    `created` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `modified` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY ('session_id') REFERENCES `server_session`(`id`) ON DELETE CASCADE

);


CREATE INDEX IF NOT EXISTS `message__owner_name` ON `message` (`owner_name`);
CREATE INDEX IF NOT EXISTS `message__from_name` ON `message` (`from_name`);
CREATE INDEX IF NOT EXISTS `message__from_role` ON `message` (`from_role`);
CREATE INDEX IF NOT EXISTS `message__to_name` ON `message` (`to_name`);
CREATE INDEX IF NOT EXISTS `message__to_role` ON `message` (`to_role`);


CREATE TABLE IF NOT EXISTS `group` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `name` TEXT NOT NULL UNIQUE,
    `owner_id` INTEGER NOT NULL,

    `members` BLOB NOT NULL,  -- list saved as JSON

    `created` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `modified` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (`owner_id`) REFERENCES `user`(`id`) ON DELETE CASCADE

);

CREATE INDEX IF NOT EXISTS `group__name` ON `group` (`name`);