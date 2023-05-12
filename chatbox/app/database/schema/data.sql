-- create default users
INSERT OR IGNORE INTO `user` (`id`,  `username`, `password`) VALUES
        (1, 'super', 1234),
        (2, 'admin', 1234);