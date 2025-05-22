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
CREATE DEFINER=`root`@`localhost` PROCEDURE `cancel_pledge`(
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
		WHERE request_id in (
			select r.request_id
			FROM (
				SELECT request.request_id
				FROM dr_events.request
				JOIN dr_events.`match` ON `match`.request_id = request.request_id
				WHERE `match`.pledge_id = param_pledge_id
				  AND `match`.shipping_status NOT IN ('shipped', 'delivered')
				  AND `match`.match_status <> 'locked match'
			) AS r
        );
    
    -- 4. Remove unlocked matches
		UPDATE dr_events.`match`
        SET canceled_flag = 1 and match_status = 'canceled match'
        WHERE `match`.match_id IN 
        (
			select m.match_id
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
CREATE DEFINER=`root`@`localhost` PROCEDURE `confirm_match`(
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
        SET status = 'locked match'
        WHERE match_id = param_match_id;
        
    -- 3. Update pledge's allocated_count
		UPDATE dr_events.pledge
        SET 
			allocated_quantity = allocated_quantity - var_quantity, 
            fulfilled_quantity = fulfilled_quantity + var_quantity
        WHERE pledge_id = var_pledge_id;
        
    -- 4. Check if fulfilled pledges matches pledged quantity
		UPDATE dr_events.pledge t
        JOIN dr_events.pledge s ON t.pledge_id = s.pledge_id
        SET t.fulfilled_flag = 1, t.pledge_status = 'fully allocated'
        WHERE pledge_id = var_pledge_id AND item_quantity = fulfilled_quantity;
        
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
/*!50003 DROP PROCEDURE IF EXISTS `create_match` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `create_match`(
	IN param_pledge_id INT,
    IN param_request_id INT,
    IN param_match_quantity INT, 
    IN param_match_status VARCHAR(50),
    IN param_match_type_id INT
)
BEGIN
	DECLARE var_full_address VARCHAR(250);
    
	DECLARE EXIT HANDLER FOR SQLEXCEPTION
	BEGIN
		ROLLBACK;
	END;
    
    START TRANSACTION;
    
     -- 1. Get User Shipping Address
		SELECT concat_ws(' ',
			   address_line1,
			   address_line2,
			   CONCAT_WS(', ',			
					city,
					state				
				), zip_code) AS full_address
		INTO var_full_address
		FROM dr_events.request
			INNER JOIN dr_admin.user ON request.user_id = user.user_id
		WHERE request_id = param_request_id;
        
	-- 1. Create Match
		INSERT INTO dr_events.`match` 
        (pledge_id, request_id, match_status, match_quantity, match_type_id, shipping_address)
        VALUES 
        (param_pledge_id, param_request_id, param_match_status, param_match_quantity, param_match_type_id, var_full_address);
        
    -- 2. Update pledge's allocated_quantity
		UPDATE dr_events.pledge
        SET allocated_quantity = allocated_quantity + param_match_quantity, pledge_status = 'partially allocated'
        WHERE pledge_id = param_pledge_id;
        
    -- 3. Update request's status
		UPDATE dr_events.request
        SET status = 'matched'
        WHERE request_id = param_request_id;
    
    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_auto_fulfill_match` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `get_auto_fulfill_match`(
	IN param_request_id INT
)
BEGIN
	DECLARE var_item_id INT;
    DECLARE var_recipient_user_id INT;   
    DECLARE var_request_quantity INT;   
    
    -- 1. Get item for request
		SELECT item_id, user_id, quantity
		INTO var_item_id, var_recipient_user_id, var_request_quantity
		FROM dr_events.request
		WHERE request.request_id = param_request_id;
        
	-- 2. Get all unfulfilled pledges that matches request's item
		SELECT 
			pledge_id
            ,pledge.user_id AS donor_id
            ,pledge.item_quantity - (pledge.allocated_quantity + pledge.fulfilled_quantity) AS pledged_items_left
            ,pledge.days_to_ship
            ,var_recipient_user_id AS recipient_id       
            ,var_request_quantity AS recipient_request_qty
		FROM dr_events.pledge
        JOIN dr_events.item ON pledge.item_id = item.item_id
		WHERE pledge.item_id = var_item_id AND pledge.fulfilled_flag = 0 AND pledge.canceled_flag = 0
			AND (pledge.item_quantity - (pledge.allocated_quantity + pledge.fulfilled_quantity) > 0);
    
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_auto_match_options` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `get_auto_match_options`(
	IN param_request_id INT
)
BEGIN
	DECLARE var_item_id INT;
    DECLARE var_recipient_user_id INT;   
    DECLARE var_request_quantity INT;  
    DECLARE var_recipient_zipcode INT; 
    
    -- 1. Get item for request
		SELECT item_id, user_id, quantity
		INTO var_item_id, var_recipient_user_id, var_request_quantity
		FROM dr_events.request
		WHERE request.request_id = param_request_id;
	
     -- 2. Get recipeint
		SELECT zip_code
		INTO var_recipient_zipcode
		FROM dr_admin.user
		WHERE user.user_id = var_recipient_user_id;
        
	-- 3. Get all unfulfilled pledges that matches request's item
		SELECT 
			pledge_id
            ,pledge.user_id AS donor_id
            ,pledge.item_quantity - (pledge.allocated_quantity + pledge.fulfilled_quantity) AS pledged_items_left
            ,pledge.days_to_ship
            ,var_recipient_user_id AS recipient_id       
            ,var_request_quantity AS recipient_request_qty
            ,var_recipient_zipcode AS recipient_zipcode
            ,donor_user.user_id AS donor_id
            ,donor_user.zip_code AS donor_zipcode
		FROM dr_events.pledge
        JOIN dr_events.item ON pledge.item_id = item.item_id
        JOIN dr_admin.user donor_user ON donor_user.user_id = pledge.user_id
		WHERE pledge.item_id = var_item_id AND pledge.fulfilled_flag = 0 AND pledge.canceled_flag = 0
			AND (pledge.item_quantity - (pledge.allocated_quantity + pledge.fulfilled_quantity) > 0)
		ORDER BY pledge.item_quantity DESC;
    
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_matches` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `get_matches`(
	IN param_user_id INT
)
BEGIN
	DECLARE var_user_role VARCHAR(50);    
    DECLARE var_zip_code VARCHAR (25);

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
        
	-- 2a. If role == 'Donor'
    IF var_user_role = 'Donor' THEN
		SELECT 
			 `match`.match_id
            ,`match`.pledge_id
			, disaster_event.event_id
            , disaster_event.event_name
			, disaster_event.location
            , item.name AS item_name
            , item.item_id
            , category.category_id
            , category.category_name           
            ,`match`.request_id
            ,`match`.match_status
            ,`match`.match_quantity
            ,`match`.created_at            
        FROM dr_events.`match`
        JOIN dr_events.request ON `match`.request_id = request.request_id
        JOIN dr_events.disaster_event ON request.event_id = disaster_event.event_id
        JOIN dr_events.category ON request.category_id = category.category_id
        JOIN dr_events.pledge ON `match`.pledge_id = pledge.pledge_id
        LEFT OUTER JOIN dr_events.item ON request.item_id = item.item_id
        WHERE pledge.user_id = param_user_id;
        
    -- 2b. If roll == 'Recipient'
    ELSEIF var_user_role = 'Recipient' THEN
		SELECT 
			 `match`.match_id
            ,`match`.pledge_id
			, disaster_event.event_id
            , disaster_event.event_name
			, disaster_event.location
            , item.name AS item_name
            , item.item_id
            , category.category_id
            , category.category_name           
            ,`match`.request_id
            ,`match`.match_status
            ,`match`.match_quantity
            ,`match`.created_at            
        FROM dr_events.`match`
        JOIN dr_events.request ON `match`.request_id = request.request_id
        JOIN dr_events.disaster_event ON request.event_id = disaster_event.event_id
        JOIN dr_events.category ON request.category_id = category.category_id
        LEFT OUTER JOIN dr_events.item ON request.item_id = item.item_id
        WHERE request.user_id = param_user_id;
        
    -- 2c. If role == 'Admin'
    ELSEIF var_user_role = 'Admin' THEN
		SELECT 
			 `match`.match_id
            ,`match`.pledge_id
			, disaster_event.event_id
            , disaster_event.event_name
			, disaster_event.location
            , item.name AS item_name
            , item.item_id
            , category.category_id
            , category.category_name           
            ,`match`.request_id
            ,`match`.match_status
            ,`match`.match_quantity
            ,`match`.created_at            
        FROM dr_events.`match`
        JOIN dr_events.request ON `match`.request_id = request.request_id
        JOIN dr_events.disaster_event ON request.event_id = disaster_event.event_id
        JOIN dr_events.category ON request.category_id = category.category_id
        LEFT OUTER JOIN dr_events.item ON request.item_id = item.item_id;
	END IF;
    
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
CREATE DEFINER=`root`@`localhost` PROCEDURE `get_pledges`(
	IN param_user_id INT
)
BEGIN
	DECLARE var_user_role VARCHAR(50);    
    DECLARE var_zip_code VARCHAR (25);

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
        
	-- 2a. If role == 'Donor'
    IF var_user_role = 'Donor' THEN
		SELECT 
			pledge.pledge_id
            ,pledge.user_id AS donor_id
            ,pledge.item_id
            ,item.name AS item_name
            ,pledge.item_quantity
            ,pledge.pledge_status
            ,pledge.fulfilled_quantity
            ,pledge.allocated_quantity
            ,pledge.item_quantity - (pledge.allocated_quantity + pledge.fulfilled_quantity) AS items_left
            ,pledge.fulfilled_quantity AS items_locked
			,pledge.allocated_quantity AS items_allocated
            ,pledge.canceled_flag
            ,pledge.fulfilled_flag
            ,pledge.created_at
            ,category.category_id
            ,category.category_name
            ,var_zip_code AS zip_code
        FROM dr_events.pledge
        JOIN dr_events.item ON pledge.item_id = item.item_id
        JOIN dr_events.category ON item.category_id = category.category_id
        WHERE pledge.user_id = param_user_id AND pledge.canceled_flag = 0;      
    -- 2b. If role == 'Admin'
    ELSEIF var_user_role = 'Admin' THEN
		SELECT 
			pledge.pledge_id
            ,pledge.user_id AS donor_id
            ,pledge.item_id
            ,item.name AS item_name
            ,pledge.item_quantity
            ,pledge.pledge_status
            ,pledge.fulfilled_quantity
            ,pledge.allocated_quantity
            ,pledge.item_quantity - (pledge.allocated_quantity + pledge.fulfilled_quantity) AS items_left
            ,pledge.fulfilled_quantity AS items_locked
			,pledge.allocated_quantity AS items_allocated
            ,pledge.canceled_flag
            ,pledge.fulfilled_flag
            ,pledge.created_at
            ,category.category_id
            ,category.category_name
            ,var_zip_code AS zip_code
        FROM dr_events.pledge
        JOIN dr_events.item ON pledge.item_id = item.item_id
        JOIN dr_events.category ON item.category_id = category.category_id
        WHERE pledge.canceled_flag = 0;
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
CREATE DEFINER=`root`@`localhost` PROCEDURE `get_requests`(
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
			request.request_id
            ,request.event_id
            ,disaster_event.event_name
            ,disaster_event.location
            ,category.category_id
            ,category.category_name
            ,item.item_id
            ,item.name AS item_name
            ,request.quantity AS request_quantity
            ,CASE WHEN current_matches.request_id IS NULL THEN request.quantity
				WHEN request.quantity - current_matches.total_matched < 0 THEN 0
				ELSE IFNULL(request.quantity, 0) - IFNULL(current_matches.total_matched, 0) END AS request_quantity_remaining
            ,request.status AS request_status
            ,request.details AS request_details
            ,var_zip_code AS requester_zipcode
        FROM dr_events.request
			JOIN dr_events.disaster_event ON request.event_id = disaster_event.event_id
			JOIN dr_events.category ON request.category_id = category.category_id        
			LEFT OUTER JOIN dr_events.item ON request.item_id = item.item_id
			LEFT OUTER JOIN
			(
				select `match`.request_id, SUM(`match`.match_quantity) AS total_matched
				from dr_events.`match`
				WHERE `match`.canceled_flag = 0
				GROUP BY `match`.request_id
			) current_matches ON request.request_id = current_matches.request_id 
        WHERE request.user_id = param_user_id;
    -- 2b. else If role anything else
    ELSEIF param_request_id IS NULL THEN
		SELECT 
			request.request_id
            ,request.event_id
            ,disaster_event.event_name
            ,disaster_event.location
            ,category.category_id
            ,category.category_name
            ,item.item_id
            ,item.name AS item_name
            ,request.quantity AS request_quantity
            ,CASE WHEN current_matches.request_id IS NULL THEN request.quantity
				WHEN request.quantity - current_matches.total_matched < 0 THEN 0
				ELSE IFNULL(request.quantity, 0) - IFNULL(current_matches.total_matched, 0) END AS request_quantity_remaining
            ,request.status AS request_status
            ,request.details AS request_details
			,var_zip_code AS requester_zipcode
        FROM dr_events.request
        JOIN dr_events.disaster_event ON request.event_id = disaster_event.event_id
        JOIN dr_events.category ON request.category_id = category.category_id        
        LEFT JOIN dr_events.item ON request.item_id = item.item_id
        LEFT OUTER JOIN
			(
				select `match`.request_id, SUM(`match`.match_quantity) AS total_matched
				from dr_events.`match`
				WHERE `match`.canceled_flag = 0
				GROUP BY `match`.request_id
			) current_matches ON request.request_id = current_matches.request_id 
        WHERE request.status not in ('fulfilled', 'canceled', 'matched');
	ELSE
		SELECT 
			request.request_id
            ,request.event_id
            ,disaster_event.event_name
            ,disaster_event.location
            ,category.category_id
            ,category.category_name
            ,item.item_id
            ,item.name AS item_name
            ,request.quantity AS request_quantity
            ,CASE WHEN current_matches.request_id IS NULL THEN request.quantity
				WHEN request.quantity - current_matches.total_matched < 0 THEN 0
				ELSE IFNULL(request.quantity, 0) - IFNULL(current_matches.total_matched, 0) END AS request_quantity_remaining
            ,request.status AS request_status
            ,request.details AS request_details
			,var_zip_code AS requester_zipcode
        FROM dr_events.request
        JOIN dr_events.disaster_event ON request.event_id = disaster_event.event_id
        JOIN dr_events.category ON request.category_id = category.category_id        
        LEFT JOIN dr_events.item ON request.item_id = item.item_id
        LEFT OUTER JOIN
			(
				select `match`.request_id, SUM(`match`.match_quantity) AS total_matched
				from dr_events.`match`
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
/*!50003 DROP PROCEDURE IF EXISTS `update_shipping_address` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `update_shipping_address`(
    IN param_match_id INT,
    IN param_shipping_address TEXT
)
BEGIN
    UPDATE dr_events.`match`
    SET shipping_address = param_shipping_address
    WHERE match_id = param_match_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `update_shipping_status` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `update_shipping_status`(
    IN param_match_id INT,
    IN param_shipping_status VARCHAR(50),
    IN param_tracking_number VARCHAR(100),
    IN param_shipping_date DATE
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
    END;
    
    START TRANSACTION;
    
    -- Update match with shipping information
    UPDATE dr_events.`match`
    SET 
        shipping_status = param_shipping_status,
        tracking_number = param_tracking_number,
        shipping_date = param_shipping_date
    WHERE match_id = param_match_id;
    
    -- If the status is shipped or delivered, lock the associated response
    IF param_shipping_status IN ('shipped', 'delivered') THEN
        UPDATE dr_events.response r
        JOIN dr_events.`match` m ON m.request_id = r.request_id
        SET r.is_locked = TRUE
        WHERE m.match_id = param_match_id;
        
        CALL confirm_match(param_match_id);
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

-- Dump completed on 2025-05-21 19:04:15
