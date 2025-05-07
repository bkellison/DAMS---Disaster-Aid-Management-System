CREATE DATABASE  IF NOT EXISTS `dr_events` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `dr_events`;
-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: dr_events
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `match`
--

DROP TABLE IF EXISTS `match`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `match` (
  `match_id` int NOT NULL AUTO_INCREMENT,
  `pledge_id` int NOT NULL,
  `request_id` int NOT NULL,
  `match_status` enum('removed match','matched','locked match') DEFAULT NULL,
  `match_quantity` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `shipping_status` enum('pending','shipped','delivered') DEFAULT 'pending',
  `shipping_date` date DEFAULT NULL,
  `tracking_number` varchar(100) DEFAULT NULL,
  `shipping_address` text,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `canceled_flag` tinyint(1) DEFAULT '0',
  `match_type_id` int DEFAULT NULL,
  PRIMARY KEY (`match_id`),
  UNIQUE KEY `match_id_UNIQUE` (`match_id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `match`
--

LOCK TABLES `match` WRITE;
/*!40000 ALTER TABLE `match` DISABLE KEYS */;
INSERT INTO `match` VALUES (28,4,6,'matched',14,'2025-04-27 23:41:23','delivered','2025-04-27','1234567','100 A ave NE','2025-04-28 00:04:55',0,NULL),(29,9,1,'matched',10,'2025-04-28 00:00:47','pending',NULL,NULL,NULL,'2025-04-28 00:00:47',0,NULL),(30,8,7,'matched',1,'2025-05-01 02:38:00','pending',NULL,NULL,NULL,'2025-05-01 02:38:00',0,4),(31,2,7,'matched',1,'2025-05-01 04:12:13','pending',NULL,NULL,NULL,'2025-05-01 04:12:13',0,2),(32,5,2,'matched',1,'2025-05-01 04:56:16','pending',NULL,NULL,NULL,'2025-05-01 04:56:16',0,4),(33,6,4,'matched',5,'2025-05-01 04:59:39','pending',NULL,NULL,NULL,'2025-05-01 04:59:39',0,4),(34,5,3,'matched',9,'2025-05-01 06:25:22','pending',NULL,NULL,NULL,'2025-05-01 06:25:22',0,2),(35,11,8,'matched',1,'2025-05-01 06:28:55','pending',NULL,NULL,NULL,'2025-05-01 06:28:55',0,4);
/*!40000 ALTER TABLE `match` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-01  1:32:34
