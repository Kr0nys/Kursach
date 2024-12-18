-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema motocycledb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema motocycledb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `motocycledb` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `motocycledb` ;

-- -----------------------------------------------------
-- Table `motocycledb`.`сотрудник`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `motocycledb`.`сотрудник` (
  `ID_сотрудника` INT NOT NULL AUTO_INCREMENT,
  `ФИО` CHAR(100) NULL DEFAULT NULL,
  `Должность` CHAR(50) NULL DEFAULT NULL,
  `Контактная_информация` CHAR(100) NULL DEFAULT NULL,
  PRIMARY KEY (`ID_сотрудника`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `motocycledb`.`поставщики`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `motocycledb`.`поставщики` (
  `ID_поставщика` INT NOT NULL AUTO_INCREMENT,
  `Детали` CHAR(100) NULL DEFAULT NULL,
  `Стоимость` CHAR(20) NULL DEFAULT NULL,
  PRIMARY KEY (`ID_поставщика`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `motocycledb`.`склад`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `motocycledb`.`склад` (
  `ID_детали` INT NOT NULL AUTO_INCREMENT,
  `Название` CHAR(100) NULL DEFAULT NULL,
  `Цена` CHAR(20) NULL DEFAULT NULL,
  `Количество_на_складе` INT NULL DEFAULT NULL,
  `поставщики_ID_поставщика` INT NOT NULL,
  PRIMARY KEY (`ID_детали`),
  INDEX `fk_склад_поставщики1_idx` (`поставщики_ID_поставщика` ASC) VISIBLE,
  CONSTRAINT `fk_склад_поставщики1`
    FOREIGN KEY (`поставщики_ID_поставщика`)
    REFERENCES `motocycledb`.`поставщики` (`ID_поставщика`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `motocycledb`.`проверка_деталей_для_сборки`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `motocycledb`.`проверка_деталей_для_сборки` (
  `ID_мотоцикла` INT NOT NULL,
  `ID_детали` INT NOT NULL,
  PRIMARY KEY (`ID_мотоцикла`),
  INDEX `ID_детали_idx` (`ID_детали` ASC) VISIBLE,
  CONSTRAINT `ID_детали`
    FOREIGN KEY (`ID_детали`)
    REFERENCES `motocycledb`.`склад` (`ID_детали`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `motocycledb`.`сборка`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `motocycledb`.`сборка` (
  `ID_сборки` INT NOT NULL AUTO_INCREMENT,
  `Дата` DATE NULL DEFAULT NULL,
  `ID_сотрудника` INT NULL DEFAULT NULL,
  `Цвет` CHAR(20) NULL DEFAULT NULL,
  `Статус` CHAR(20) NULL DEFAULT NULL,
  `ID_мотоцикла` INT NOT NULL,
  PRIMARY KEY (`ID_сборки`),
  INDEX `ID_сотрудника` (`ID_сотрудника` ASC) VISIBLE,
  INDEX `fk_сборка_проверка_деталей_для_сб_idx` (`ID_мотоцикла` ASC) VISIBLE,
  CONSTRAINT `сборка_ibfk_1`
    FOREIGN KEY (`ID_сотрудника`)
    REFERENCES `motocycledb`.`сотрудник` (`ID_сотрудника`),
  CONSTRAINT `fk_сборка_проверка_деталей_для_сбо1`
    FOREIGN KEY (`ID_мотоцикла`)
    REFERENCES `motocycledb`.`проверка_деталей_для_сборки` (`ID_мотоцикла`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `motocycledb`.`мотоцикл`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `motocycledb`.`мотоцикл` (
  `ID_мотоцикла` INT NOT NULL AUTO_INCREMENT,
  `Модель` CHAR(50) NULL DEFAULT NULL,
  `Цвет` CHAR(20) NULL DEFAULT NULL,
  `Категория` CHAR(50) NULL DEFAULT NULL,
  `Дата_выпуска` DATE NULL DEFAULT NULL,
  `С_С_комплектующих` CHAR(50) NULL DEFAULT NULL,
  `Фотография` BLOB NULL DEFAULT NULL,
  `ID_сборки` INT NULL DEFAULT NULL,
  PRIMARY KEY (`ID_мотоцикла`),
  INDEX `ID_сборки_idx` (`ID_сборки` ASC) VISIBLE,
  CONSTRAINT `ID_сборки`
    FOREIGN KEY (`ID_сборки`)
    REFERENCES `motocycledb`.`сборка` (`ID_сборки`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
