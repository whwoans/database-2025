CREATE DATABASE IF NOT EXISTS test
DEFAULT CHARACTER SET utf8mb4
DEFAULT COLLATE utf8mb4_unicode_ci;

USE test;

CREATE TABLE `menu` (
	`id`	int	NOT NULL,
	`store_id`	int	NOT NULL,
	`menu`	string(200)	NOT NULL,
	`price`	int	NOT NULL,
	`created_at`	datetime	NOT NULL,
	`update_at`	datetime	NULL
);

CREATE TABLE `review` (
	`id`	int	NOT NULL,
	`user_id`	int	NOT NULL,
	`store_id`	int	NOT NULL,
	`order_id`	int	NULL,
	`rating`	int	NOT NULL,
	`content`	string(200)	NULL,
	`created_at`	datetime	NOT NULL,
	`update_at`	datetime	NULL
);

CREATE TABLE `order` (
	`id`	int	NOT NULL,
	`user_id`	int	NOT NULL,
	`store_id`	int	NOT NULL,
	`rider_id`	int	NOT NULL,
	`order`	string(100)	NOT NULL,
	`total_price`	int	NOT NULL,
	`order_time`	datetime	NOT NULL
);

CREATE TABLE `favorite` (
	`id`	int	NOT NULL,
	`user_id`	int	NOT NULL,
	`store_id`	int	NOT NULL,
	`created_at`	datetime	NOT NULL,
	`is_deleted`	boolen	NOT NULL
);

CREATE TABLE `rider` (
	`id`	int	NOT NULL,
	`rider_id`	string(30)	NOT NULL,
	`phone`	string(20)	NOT NULL,
	`vehicle`	string(30)	NOT NULL
);

CREATE TABLE `payment` (
	`id`	int	NOT NULL,
	`payment`	varchar(30)	NOT NULL
);

CREATE TABLE `owner` (
	`id`	int	NOT NULL,
	`owner_id`	string(30)	NOT NULL,
	`owner_passwd`	string(50)	NOT NULL,
	`email`	string(30)	NOT NULL
);

CREATE TABLE `coupon` (
	`id`	int	NOT NULL,
	`store_id`	int	NOT NULL,
	`period`	int	NULL,
	`discount`	int	NULL,
	`is_deleted`	boolen	NOT NULL
);

CREATE TABLE `category` (
	`id`	int	NOT NULL,
	`category`	string(30)	NOT NULL
);

CREATE TABLE `user` (
	`id`	int	NOT NULL,
	`user_id`	string(30)	NOT NULL,
	`passwd`	string(50)	NOT NULL,
	`email`	string(30)	NOT NULL,
	`name`	string(100)	NOT NULL,
	`address`	string(100)	NOT NULL,
	`created_at`	datetime	NOT NULL,
	`update_at`	datetime	NOT NULL
);

CREATE TABLE `store` (
	`id`	int	NOT NULL,
	`owner_id`	int	NOT NULL,
	`category_id`	int	NOT NULL,
	`payment_id`	int	NULL,
	`store_name`	Varchar(50)	NOT NULL,
	`category`	string(30)	NOT NULL,
	`phone`	string(20)	NOT NULL,
	`minprice`	string(30)	NOT NULL,
	`reviewCount`	int	NOT NULL,
	`operationTime`	string(250)	NOT NULL,
	`closedDay`	string(250)	NOT NULL,
	`information` string(500) NOT NULL,
	`created_at`	datetime	NOT NULL,
	`update_at`	datetime	NULL
);

ALTER TABLE `menu` ADD CONSTRAINT `PK_MENU` PRIMARY KEY (
	`id`
);

ALTER TABLE `review` ADD CONSTRAINT `PK_REVIEW` PRIMARY KEY (
	`id`
);

ALTER TABLE `order` ADD CONSTRAINT `PK_ORDER` PRIMARY KEY (
	`id`
);

ALTER TABLE `favorite` ADD CONSTRAINT `PK_favorite` PRIMARY KEY (
	`id`
);

ALTER TABLE `rider` ADD CONSTRAINT `PK_RIDER` PRIMARY KEY (
	`id`
);

ALTER TABLE `payment` ADD CONSTRAINT `PK_PAYMENT` PRIMARY KEY (
	`id`
);

ALTER TABLE `owner` ADD CONSTRAINT `PK_OWNER` PRIMARY KEY (
	`id`
);

ALTER TABLE `coupon` ADD CONSTRAINT `PK_COUPON` PRIMARY KEY (
	`id`
);

ALTER TABLE `category` ADD CONSTRAINT `PK_CATEGORY` PRIMARY KEY (
	`id`
);

ALTER TABLE `user` ADD CONSTRAINT `PK_USER` PRIMARY KEY (
	`id`
);

ALTER TABLE `store` ADD CONSTRAINT `PK_STORE` PRIMARY KEY (
	`id`
);

-- 외래키 제약조건
ALTER TABLE `store` ADD CONSTRAINT `FK_STORE_PAYMENT` FOREIGN KEY (`payment_id`) REFERENCES `payment` (`id`);
ALTER TABLE `review` ADD CONSTRAINT `FK_REVIEW_STORE` FOREIGN KEY (`store_id`) REFERENCES `store` (`id`);
ALTER TABLE `review` ADD CONSTRAINT `FK_REVIEW_ORDER` FOREIGN KEY (`order_id`) REFERENCES `order` (`id`);

-- 기본 지불방식 데이터 추가
INSERT INTO `payment` (`payment`) VALUES
('만나서 카드결제'),
('만나서 현금 결제');

-- 기본 카테고리 데이터 추가
INSERT INTO `category` (`category`) VALUES
('한식'),
('일식'),
('중식'),
('양식'),
('분식'),
('패스트푸드');
