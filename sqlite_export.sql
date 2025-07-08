-- Export SQLite vers MySQL
-- Généré le: 2025-07-07 15:02:28
-- Base source: C:\Users\danie\qrcode-chronoscan-analytics\backendqrcode\instance\qrcode_users.db

-- Configuration MySQL
SET FOREIGN_KEY_CHECKS = 0;
SET AUTOCOMMIT = 0;
START TRANSACTION;

-- ============================================
-- CRÉATION DES TABLES
-- ============================================

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `email_verified` tinyint(1) DEFAULT '1',
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `last_login` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `qr_codes`;
CREATE TABLE `qr_codes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `type` varchar(20) NOT NULL,
  `data` text NOT NULL,
  `original_url` text,
  `color` varchar(7) DEFAULT '#000000',
  `background_color` varchar(7) DEFAULT '#ffffff',
  `size` int DEFAULT '256',
  `is_dynamic` tinyint(1) DEFAULT '0',
  `short_code` varchar(10) DEFAULT NULL,
  `short_url` varchar(255) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'active',
  `scans` int DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `expires_at` datetime DEFAULT NULL,
  `validity_duration` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `short_code` (`short_code`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `qr_codes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `short_links`;
CREATE TABLE `short_links` (
  `short_code` varchar(10) NOT NULL,
  `original_url` text NOT NULL,
  `qr_code_id` int DEFAULT NULL,
  `clicks` int DEFAULT '0',
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`short_code`),
  KEY `qr_code_id` (`qr_code_id`),
  CONSTRAINT `short_links_ibfk_1` FOREIGN KEY (`qr_code_id`) REFERENCES `qr_codes` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `qr_scan_logs`;
CREATE TABLE `qr_scan_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `qr_code_id` int NOT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text,
  `device_type` varchar(50) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `scanned_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `qr_code_id` (`qr_code_id`),
  CONSTRAINT `qr_scan_logs_ibfk_1` FOREIGN KEY (`qr_code_id`) REFERENCES `qr_codes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `refresh_tokens`;
CREATE TABLE `refresh_tokens` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `token_hash` varchar(255) NOT NULL,
  `expires_at` datetime NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `is_revoked` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `token_hash` (`token_hash`),
  CONSTRAINT `refresh_tokens_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- INSERTION DES DONNÉES
-- ============================================

-- Utilisateurs
INSERT INTO `users` VALUES (1, 'test@example.com', 'pbkdf2:sha256:600000$Hnl9VbV7AwvdIj7U$58f7ac66e76c7964b1db69105700d87265c527750a6a8b2c7329ce6b58541bf9', 1, NULL, NULL, NULL, NULL, 0, NULL, 1, '2025-07-07 14:40:30.927364', '2025-07-07 14:40:30.927364', NULL);

-- QR Codes
INSERT INTO `qr_codes` VALUES ('r7WpqBiFsnuxiaOKYhqNsA', 1, 'url', 'https://www.google.com', NULL, '#000000', '#ffffff', 256, 0, NULL, NULL, 'active', 5, '2025-07-07 14:40:30.941585', '2025-07-07 14:40:30.941585', '2025-08-06 14:40:30.941280', '30_days');
INSERT INTO `qr_codes` VALUES ('QGMj97vRXXFMZmCtl238Gw', 1, 'url', 'http://localhost:5000/s/A04ECp', 'https://www.github.com', '#1a73e8', '#ffffff', 512, 1, 'A04ECp', 'http://localhost:5000/s/A04ECp', 'active', 12, '2025-07-07 14:40:30.941585', '2025-07-07 14:40:30.941585', '2025-09-05 14:40:30.941585', '60_days');
INSERT INTO `qr_codes` VALUES ('xuBaDKhlybFrcXh_1JlljQ', 1, 'text', 'Bonjour! Ceci est un QR code de test avec du texte.', NULL, '#d93025', '#ffffff', 256, 0, NULL, NULL, 'active', 3, '2025-07-07 14:40:30.941585', '2025-07-07 14:40:30.941585', '2025-07-14 14:40:30.941585', '7_days');

-- Liens courts
INSERT INTO `short_links` VALUES (1, 'A04ECp', 'https://www.github.com', 'QGMj97vRXXFMZmCtl238Gw', 8, 1, '2025-07-07 14:40:30.954377', '2025-07-07 14:40:30.954377');

-- Logs de scan
INSERT INTO `qr_scan_logs` VALUES (1, 'r7WpqBiFsnuxiaOKYhqNsA', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', NULL, 'FR', 'desktop', '2025-07-07 12:40:30.950092');
INSERT INTO `qr_scan_logs` VALUES (2, 'QGMj97vRXXFMZmCtl238Gw', '10.0.0.50', 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)', NULL, 'FR', 'mobile', '2025-07-07 14:10:30.950092');
INSERT INTO `qr_scan_logs` VALUES (3, 'xuBaDKhlybFrcXh_1JlljQ', '172.16.0.25', 'Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X)', NULL, 'FR', 'tablet', '2025-07-07 14:35:30.950092');

-- ============================================
-- FIN DE L'EXPORT
-- ============================================

COMMIT;
SET FOREIGN_KEY_CHECKS = 1;
SET AUTOCOMMIT = 1;
