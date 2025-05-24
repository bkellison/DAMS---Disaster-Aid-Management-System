CREATE DATABASE  IF NOT EXISTS `dr_events` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `dr_events`;
-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: nozomi.proxy.rlwy.net    Database: dr_events
-- ------------------------------------------------------
-- Server version	9.3.0

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
-- Dumping events for database 'dr_events'
--

--
-- Dumping routines for database 'dr_events'
--
/*!50003 DROP PROCEDURE IF EXISTS `cancel_pledge` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `cancel_pledge`(
	IN param_pledge_id INT
)
BEGIN
	DECLARE var_fulfilled_quantity INT;
    DECLARE var_allocated_quantity INT;
    
	DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
		ROLLBACK;
	END;
    
    START TRANSACTION;
    
    -- 1. Check the pledge
		SELECT fulfilled_quantity, allocated_quantity
		INTO var_fulfilled_quantity, var_allocated_quantity
		FROM dr_events.pledge
		WHERE pledge_id = param_pledge_id;
        
	-- 2. Cancel Pledge
		UPDATE dr_events.pledge
		SET canceled_flag = 1
		WHERE pledge_id = param_pledge_id;
        
	-- 3. Update Request
		UPDATE dr_events.request
        SET status = 'pending'
		WHERE request_id IN (
			SELECT r.request_id
			FROM (
				SELECT request.request_id
				FROM dr_events.request
				JOIN dr_events.`match` ON `match`.request_id = request.request_id
				WHERE `match`.pledge_id = param_pledge_id
				  AND `match`.shipping_status NOT IN ('shipped', 'delivered')
				  AND `match`.match_status <> 'locked match'
			) AS r
        );
    
    -- 4. Remove unlocked matches (FIXED: Separate SET clauses)
		UPDATE dr_events.`match`
        SET canceled_flag = 1, match_status = 'canceled match'
        WHERE `match`.match_id IN 
        (
			SELECT m.match_id
			FROM (
				SELECT `match`.match_id
				FROM dr_events.`match`
				WHERE `match`.pledge_id = param_pledge_id
				  AND `match`.shipping_status NOT IN ('shipped', 'delivered')
				  AND `match`.match_status <> 'locked match'
			) AS m
        );
        
	COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `confirm_match` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `confirm_match`(
	IN param_match_id INT
)
BEGIN
	DECLARE var_pledge_id INT;
    DECLARE var_match_quantity INT;
    DECLARE var_request_id INT;
    DECLARE var_request_quantity INT;

	DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
		ROLLBACK;
	END;
    
    START TRANSACTION;
    
    -- 1. Get pledge id and quantity from match
		SELECT pledge_id, match_quantity, request_id
        INTO var_pledge_id, var_match_quantity, var_request_id
        FROM dr_events.`match`
        WHERE match_id = param_match_id;
    
	-- 2. Update Match Status
		UPDATE dr_events.`match` 
        SET match_status = 'locked match'
        WHERE match_id = param_match_id;
        
    -- 3. Update pledge's allocated_count (only if pledge_id is not null)
    IF var_pledge_id IS NOT NULL THEN
		UPDATE dr_events.pledge
        SET 
			allocated_quantity = allocated_quantity - var_match_quantity, 
            fulfilled_quantity = fulfilled_quantity + var_match_quantity
        WHERE pledge_id = var_pledge_id;
        
        -- 4. Check if fulfilled pledges matches pledged quantity
		UPDATE dr_events.pledge t
        JOIN dr_events.pledge s ON t.pledge_id = s.pledge_id
        SET t.fulfilled_flag = 1, t.pledge_status = 'fully allocated'
        WHERE t.pledge_id = var_pledge_id AND s.item_quantity = s.fulfilled_quantity;
    END IF;
        
	-- 5. Update request's status
		UPDATE dr_events.request
        SET status = 'fulfilled'
        WHERE request_id = var_request_id;
    
    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_pledges` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `get_pledges`(
	IN param_user_id INT
)
BEGIN
	DECLARE var_user_role VARCHAR(50);    
    DECLARE var_zip_code VARCHAR(25);

	DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
            @sqlstate = RETURNED_SQLSTATE, 
            @errno = MYSQL_ERRNO, 
            @text = MESSAGE_TEXT;
        SELECT @sqlstate, @errno, @text;
		ROLLBACK;
	END;
    
    START TRANSACTION;
    
    -- 1. Check the users role and get their zipcode
		SELECT `role`, zip_code
		INTO var_user_role, var_zip_code
		FROM dr_admin.user
		WHERE user_id = param_user_id;
        
	-- 2a. If role == 'Donor'
    IF var_user_role = 'Donor' THEN
		SELECT 
			pledge.pledge_id,
            pledge.user_id AS donor_id,
            pledge.item_id,
            item.name AS item_name,
            pledge.item_quantity,
            pledge.pledge_status,
            pledge.fulfilled_quantity,
            pledge.allocated_quantity,
            pledge.item_quantity - (pledge.allocated_quantity + pledge.fulfilled_quantity) AS items_left,
            pledge.fulfilled_quantity AS items_locked,
			pledge.allocated_quantity AS items_allocated,
            pledge.canceled_flag,
            pledge.fulfilled_flag,
            pledge.created_at,
            category.category_id,
            category.category_name,
            var_zip_code AS zip_code
        FROM dr_events.pledge
        JOIN dr_events.item ON pledge.item_id = item.item_id
        JOIN dr_events.category ON item.category_id = category.category_id
        WHERE pledge.user_id = param_user_id AND pledge.canceled_flag = 0;
        
    -- 2b. If role == 'Admin'
    ELSEIF var_user_role = 'Admin' THEN
		SELECT 
			pledge.pledge_id,
            pledge.user_id AS donor_id,
            pledge.item_id,
            item.name AS item_name,
            pledge.item_quantity,
            pledge.pledge_status,
            pledge.fulfilled_quantity,
            pledge.allocated_quantity,
            pledge.item_quantity - (pledge.allocated_quantity + pledge.fulfilled_quantity) AS items_left,
            pledge.fulfilled_quantity AS items_locked,
			pledge.allocated_quantity AS items_allocated,
            pledge.canceled_flag,
            pledge.fulfilled_flag,
            pledge.created_at,
            category.category_id,
            category.category_name,
            donor_user.zip_code AS zip_code
        FROM dr_events.pledge
        JOIN dr_events.item ON pledge.item_id = item.item_id
        JOIN dr_events.category ON item.category_id = category.category_id
        JOIN dr_admin.user donor_user ON pledge.user_id = donor_user.user_id
        WHERE pledge.canceled_flag = 0;
        
    -- 2c. For any other role (shouldn't happen, but handle gracefully)
    ELSE
        SELECT 
			pledge.pledge_id,
            pledge.user_id AS donor_id,
            pledge.item_id,
            item.name AS item_name,
            pledge.item_quantity,
            pledge.pledge_status,
            pledge.fulfilled_quantity,
            pledge.allocated_quantity,
            pledge.item_quantity - (pledge.allocated_quantity + pledge.fulfilled_quantity) AS items_left,
            pledge.fulfilled_quantity AS items_locked,
			pledge.allocated_quantity AS items_allocated,
            pledge.canceled_flag,
            pledge.fulfilled_flag,
            pledge.created_at,
            category.category_id,
            category.category_name,
            var_zip_code AS zip_code
        FROM dr_events.pledge
        JOIN dr_events.item ON pledge.item_id = item.item_id
        JOIN dr_events.category ON item.category_id = category.category_id
        WHERE pledge.user_id = param_user_id AND pledge.canceled_flag = 0;
	END IF;
    
    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_requests` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `get_requests`(
	IN param_user_id INT,
    IN param_request_id INT
)
BEGIN
	DECLARE var_user_role VARCHAR(50);    
    DECLARE var_zip_code VARCHAR(25);    

	DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
		ROLLBACK;
	END;
    
    START TRANSACTION;
    
    -- 1. Check the users role
		SELECT `role`, zip_code
		INTO var_user_role, var_zip_code
		FROM dr_admin.user
		WHERE user_id = param_user_id;
        
	-- 2a. If role == 'Recipient'
    IF var_user_role = 'Recipient' THEN
		SELECT 
			request.request_id,
            request.event_id,
            disaster_event.event_name,
            disaster_event.location,
            category.category_id,
            category.category_name,
            item.item_id,
            item.name AS item_name,
            request.quantity AS request_quantity,
            request.preferred_match_type_id,
            mt.name AS preferred_match_type_name,
            CASE WHEN current_matches.request_id IS NULL THEN request.quantity
				WHEN request.quantity - current_matches.total_matched < 0 THEN 0
				ELSE IFNULL(request.quantity, 0) - IFNULL(current_matches.total_matched, 0) END AS request_quantity_remaining,
            request.status AS request_status,
            request.details AS request_details,
            var_zip_code AS requester_zipcode
        FROM dr_events.request
			JOIN dr_events.disaster_event ON request.event_id = disaster_event.event_id
			JOIN dr_events.category ON request.category_id = category.category_id        
			LEFT OUTER JOIN dr_events.item ON request.item_id = item.item_id
            LEFT OUTER JOIN dr_events.match_type mt ON request.preferred_match_type_id = mt.match_type_id
			LEFT OUTER JOIN
			(
				SELECT `match`.request_id, SUM(`match`.match_quantity) AS total_matched
				FROM dr_events.`match`
				WHERE `match`.canceled_flag = 0
				GROUP BY `match`.request_id
			) current_matches ON request.request_id = current_matches.request_id 
        WHERE request.user_id = param_user_id;
        
    -- 2b. If param_request_id is NULL (get all non-fulfilled requests)
    ELSEIF param_request_id IS NULL THEN
		SELECT 
			request.request_id,
            request.user_id,
            request.event_id,
            disaster_event.event_name,
            disaster_event.location,
            category.category_id,
            category.category_name,
            item.item_id,
            item.name AS item_name,
            request.quantity AS request_quantity,
            request.preferred_match_type_id,
            mt.name AS preferred_match_type_name,
            CASE WHEN current_matches.request_id IS NULL THEN request.quantity
				WHEN request.quantity - current_matches.total_matched < 0 THEN 0
				ELSE IFNULL(request.quantity, 0) - IFNULL(current_matches.total_matched, 0) END AS request_quantity_remaining,
            request.status AS request_status,
            request.details AS request_details,
			user.zip_code AS requester_zipcode
        FROM dr_events.request
        JOIN dr_events.disaster_event ON request.event_id = disaster_event.event_id
        JOIN dr_events.category ON request.category_id = category.category_id
        JOIN dr_admin.user ON request.user_id = user.user_id        
        LEFT JOIN dr_events.item ON request.item_id = item.item_id
        LEFT OUTER JOIN dr_events.match_type mt ON request.preferred_match_type_id = mt.match_type_id
        LEFT OUTER JOIN
			(
				SELECT `match`.request_id, SUM(`match`.match_quantity) AS total_matched
				FROM dr_events.`match`
				WHERE `match`.canceled_flag = 0
				GROUP BY `match`.request_id
			) current_matches ON request.request_id = current_matches.request_id 
        WHERE request.status NOT IN ('fulfilled', 'canceled');
        
	-- 2c. Get specific request by ID
	ELSE
		SELECT 
			request.request_id,
            request.user_id,
            request.event_id,
            disaster_event.event_name,
            disaster_event.location,
            category.category_id,
            category.category_name,
            item.item_id,
            item.name AS item_name,
            request.quantity AS request_quantity,
            request.preferred_match_type_id,
            mt.name AS preferred_match_type_name,
            CASE WHEN current_matches.request_id IS NULL THEN request.quantity
				WHEN request.quantity - current_matches.total_matched < 0 THEN 0
				ELSE IFNULL(request.quantity, 0) - IFNULL(current_matches.total_matched, 0) END AS request_quantity_remaining,
            request.status AS request_status,
            request.details AS request_details,
			user.zip_code AS requester_zipcode
        FROM dr_events.request
        JOIN dr_events.disaster_event ON request.event_id = disaster_event.event_id
        JOIN dr_events.category ON request.category_id = category.category_id
        JOIN dr_admin.user ON request.user_id = user.user_id
        LEFT JOIN dr_events.item ON request.item_id = item.item_id
        LEFT OUTER JOIN dr_events.match_type mt ON request.preferred_match_type_id = mt.match_type_id
        LEFT OUTER JOIN
			(
				SELECT `match`.request_id, SUM(`match`.match_quantity) AS total_matched
				FROM dr_events.`match`
				WHERE `match`.canceled_flag = 0
				GROUP BY `match`.request_id
			) current_matches ON request.request_id = current_matches.request_id 
        WHERE request.request_id = param_request_id;
	END IF;
    
    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-23 22:12:13
