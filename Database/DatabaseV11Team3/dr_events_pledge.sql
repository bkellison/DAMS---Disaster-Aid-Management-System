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
-- Table structure for table `pledge`
--

DROP TABLE IF EXISTS `pledge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pledge` (
  `pledge_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `item_id` int DEFAULT NULL,
  `item_quantity` int DEFAULT NULL,
  `pledge_status` enum('offered','partially allocated','fully allocated','canceled','partially canceled') DEFAULT 'offered',
  `fulfilled_quantity` int DEFAULT '0',
  `allocated_quantity` int DEFAULT '0',
  `canceled_flag` tinyint(1) DEFAULT '0',
  `fulfilled_flag` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `days_to_ship` int DEFAULT NULL,
  PRIMARY KEY (`pledge_id`),
  UNIQUE KEY `pledge_id_UNIQUE` (`pledge_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pledge`
--

LOCK TABLES `pledge` WRITE;
/*!40000 ALTER TABLE `pledge` DISABLE KEYS */;
INSERT INTO `pledge` VALUES (1,4,1,10,'offered',0,10,0,0,'2025-04-22 06:24:51',NULL),(2,4,2,2,'partially allocated',0,1,0,0,'2025-04-22 06:57:20',NULL),(3,4,3,1,'offered',0,0,0,0,'2025-04-22 06:58:08',NULL),(4,4,1,20,'offered',0,14,0,0,'2025-04-22 06:59:02',NULL),(5,4,1,56,'partially allocated',0,10,0,0,'2025-04-22 07:00:30',NULL),(6,17,1,5,'partially allocated',0,5,0,0,'2025-04-27 01:44:58',NULL),(7,17,2,5,'offered',0,5,0,0,'2025-04-27 05:29:59',NULL),(8,17,2,9,'partially allocated',0,1,0,0,'2025-04-27 06:20:04',NULL),(9,17,3,20,'offered',0,10,0,0,'2025-04-27 23:59:45',NULL),(10,11,4,15,'offered',0,0,1,0,'2025-04-30 00:18:45',5),(11,11,8,3,'partially allocated',0,1,0,0,'2025-04-30 04:15:23',2),(12,11,3,8,'offered',0,0,0,0,'2025-04-30 04:15:35',1);
/*!40000 ALTER TABLE `pledge` ENABLE KEYS */;
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
