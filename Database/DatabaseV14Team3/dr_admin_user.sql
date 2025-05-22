CREATE DATABASE  IF NOT EXISTS `dr_admin` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `dr_admin`;
-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: dr_admin
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
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `password` binary(60) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `role` enum('Admin','Donor','Recipient','Call Center Operator') NOT NULL,
  `zip_code` varchar(10) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `is_approved` tinyint(1) NOT NULL DEFAULT '1',
  `address_line1` varchar(250) DEFAULT NULL,
  `address_line2` varchar(100) DEFAULT NULL,
  `city` varchar(250) DEFAULT NULL,
  `state` varchar(150) DEFAULT NULL,
  `country` varchar(150) DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (4,'vmkelly',_binary '$2b$12$8PILzI/bbydlpD4nD/4LKeFIquhBSqMa8K27.K6MnHvYzWvIGxFEe','test@email.com','Admin','52040',1,1,NULL,NULL,NULL,NULL,NULL),(11,'vmarykelly',_binary '$2b$12$rvze.1Ms0GoFdd44uwrCvORm5TiNNtQedhZpL8OS4xuS6mbQXMHry','testing@email.com','Donor','52401',1,1,NULL,NULL,NULL,NULL,NULL),(12,'veronica.kelly',_binary '$2b$12$4IBJ0OWKoGR4smFvTsfz2u4UnneXn/BlDbgqUgDxTP5jQUytmdLNi','tester@email.com','Recipient','52040',1,1,'788 12th Ave SE',NULL,'Dyersville','IA',NULL),(13,'veronica.mkelly',_binary '$2b$12$CTiwH3KixO.a6jSpeYQHneBtiJGvaWCa.gt2JSv3.6VLJHVcS2n/e','veronica.mkelly@test.com','Admin','48756',1,1,NULL,NULL,NULL,NULL,NULL),(14,'newadmin.test',_binary '$2b$12$2KYCHK9o9KiAHB184O5HQuzkL5q3b8sLNVPIlj/2eCOozDtgnO1Hu','newadmin.test@email.com','Admin','68954',1,1,NULL,NULL,NULL,NULL,NULL),(15,'bkellison',_binary '$2b$12$8/8qopy0DuRH7joiaNJuauItK9eOdmSBA7IEhvye0zDQfU9ohgee2','kellisonblake@gmail.com','Admin','52411',1,1,NULL,NULL,NULL,NULL,NULL),(16,'bkellison1',_binary '$2b$12$4.2ZFD3.AUPvpqm6FRAw/eWxxBQCLAj115lxPXhqTTSw7BAOs5gBC','bkellison@uiowa.edu','Recipient','52411',1,1,NULL,NULL,NULL,NULL,NULL),(17,'bkellison2',_binary '$2b$12$HtH1kOY/EcorIKUojbgj/exB3pE6acL34EWrgXV/lBWzcc87DToD2','kellisonblake@gmail.com','Donor','52411',1,1,NULL,NULL,NULL,NULL,NULL),(18,'vkelly',_binary '$2b$12$6LCLZo6MWV0EuyTC9mpzA.HVK8YU3qMXTd/LZpaIfpzQuh/9ZqzbK','veronica.kelly@outlook.com','Recipient','52401',1,0,NULL,NULL,NULL,NULL,NULL),(19,'kelly.test',_binary '$2b$12$eX0RTwUAqoVCood51SpFR.A1XqxO4NeQ366fOo9KR25WuzEivi4Ti','kelly.test@test.com','Recipient','52227',1,0,'788 4th St. NW','','Ely','IA',NULL);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-21 19:04:15
