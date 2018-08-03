-- MySQL dump 10.13  Distrib 5.7.17, for macos10.12 (x86_64)
--
-- Host: localhost    Database: DWI
-- ------------------------------------------------------
-- Server version	8.0.11

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Compounding`
--

DROP TABLE IF EXISTS `Compounding`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Compounding` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `RPO` varchar(45) NOT NULL,
  `Bin` varchar(45) NOT NULL,
  `Machine` varchar(45) NOT NULL,
  `Output` varchar(45) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=108 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Compounding`
--

LOCK TABLES `Compounding` WRITE;
/*!40000 ALTER TABLE `Compounding` DISABLE KEYS */;
INSERT INTO `Compounding` VALUES (1,'RPO-111111','B07','COMP','SL-DW-01'),(2,'RPO-111111','B14','COMP','SL-DW-01'),(3,'RPO-111111','A12','COMP','SL-DW-01'),(4,'RPO-111111','A06','COMP','SL-DW-01'),(5,'RPO-111111','A09','COMP','SL-DW-01'),(6,'RPO-222222','CF03','COMP','SL-DW-19'),(7,'RPO-222222','B15','COMP','SL-DW-19'),(8,'RPO-222222','B11','COMP','SL-DW-19'),(9,'RPO-222222','A06','COMP','SL-DW-19'),(16,'RPO-222222','A09','COMP','SL-DW-19'),(17,'RPO-222222','A12','COMP','SL-DW-19'),(107,'RPO-111111','CF03','COMP','SL-DW-01');
/*!40000 ALTER TABLE `Compounding` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Location`
--

DROP TABLE IF EXISTS `Location`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Location` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Bin` varchar(45) NOT NULL,
  `x` int(11) NOT NULL,
  `y` int(11) NOT NULL,
  `Width` int(11) NOT NULL,
  `Height` int(11) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Location`
--

LOCK TABLES `Location` WRITE;
/*!40000 ALTER TABLE `Location` DISABLE KEYS */;
INSERT INTO `Location` VALUES (1,'B07',405,582,10,100),(2,'B14',188,583,10,100),(3,'A12',723,552,10,140),(4,'A06',902,438,10,250),(5,'A09',813,438,10,250),(6,'COMP',266,59,150,80),(7,'SL-DW-01',157,155,10,50),(14,'CF03',88,271,10,100),(15,'B15',150,583,10,100),(16,'B11',278,583,10,100),(17,'SL-DW-19',151,47,250,10),(18,'C0400',55,73,65,30),(19,'C02',59,277,10,40),(20,'CF05',133,263,10,125),(21,'B14',188,583,10,100),(22,'B13',227,583,10,100),(23,'B12',239,583,10,100),(24,'B10',316,583,10,100),(25,'B09',329,583,10,100),(26,'B08',367,583,10,100),(27,'A11',762,438,10,250),(28,'A10',775,438,10,250),(29,'A08',852,438,10,250),(30,'A07',865,438,10,250),(31,'A05',941,438,10,250),(32,'A04',954,438,10,250),(33,'A03',991,438,10,250);
/*!40000 ALTER TABLE `Location` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Pick`
--

DROP TABLE IF EXISTS `Pick`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Pick` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `RPO` varchar(45) NOT NULL,
  `Item` varchar(45) NOT NULL,
  `Bin` varchar(45) NOT NULL,
  `Quantity` varchar(45) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Id_UNIQUE` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Pick`
--

LOCK TABLES `Pick` WRITE;
/*!40000 ALTER TABLE `Pick` DISABLE KEYS */;
INSERT INTO `Pick` VALUES (1,'RPO-111111','001','B07','100'),(2,'RPO-111111','002','B14','120'),(3,'RPO-111111','003','A12','130'),(4,'RPO-111111','004','A06','140'),(5,'RPO-111111','005','A09','150'),(6,'RPO-111111','006','CF03','160');
/*!40000 ALTER TABLE `Pick` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Summary`
--

DROP TABLE IF EXISTS `Summary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Summary` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `RPO` varchar(45) NOT NULL,
  `Status` varchar(45) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `RPO_UNIQUE` (`RPO`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Summary`
--

LOCK TABLES `Summary` WRITE;
/*!40000 ALTER TABLE `Summary` DISABLE KEYS */;
INSERT INTO `Summary` VALUES (1,'RPO-999999','Done'),(2,'RPO-888888','Done'),(3,'RPO-777777','Done'),(4,'RPO-666666','Done'),(5,'RPO-555555','Done'),(6,'RPO-444444','Waiting'),(7,'RPO-333333','Waiting'),(8,'RPO-123456','Done'),(9,'RPO-654321','Done'),(10,'RPO-213312','Done'),(29,'RPO-111111','Done');
/*!40000 ALTER TABLE `Summary` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-08-03 15:39:11
