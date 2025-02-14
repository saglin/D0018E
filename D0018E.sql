CREATE TABLE `User` (
  `id` integer PRIMARY KEY NOT NULL,
  `username` varchar(50) NOT NULL,
  `encrypted_password` varchar(100) NOT NULL,
  `firstname` varchar(50),
  `lastname` varchar(50),
  `email` varchar(100) UNIQUE,
  `phone_number` varchar(100),
  `adress` varchar(100),
  `is_admin` bool DEFAULT false
);

CREATE TABLE `Item` (
  `id` integer PRIMARY KEY NOT NULL,
  `item_name` varchar(255),
  `price` integer,
  `stock` integer,
  `item_description` varchar(5000),
  `item_image` varchar(255) COMMENT 'file path to image'
);

CREATE TABLE `Shopping_Cart` (
  `user_id` integer,
  `item_id` integer,
  `item_amount` integer,
  PRIMARY KEY (`user_id`, `item_id`)
);

CREATE TABLE `Order` (
  `id` integer PRIMARY KEY,
  `user_id` integer,
  `date_placed` date,
  `sent` bool DEFAULT false
);

CREATE TABLE `Order_Items` (
  `item_id` integer,
  `order_id` integer,
  `item_amount` integer,
  `price` integer,
  PRIMARY KEY (`item_id`, `order_id`)
);

CREATE TABLE `Comment` (
  `id` integer PRIMARY KEY,
  `user_id` integer,
  `time_posted` date,
  `item_id` integer,
  `comment_text` varchar(1000)
);

CREATE TABLE `Rating` (
  `user_id` integer,
  `item_id` integer,
  `star_rating` integer(5),
  PRIMARY KEY (`user_id`, `item_id`)
);

ALTER TABLE `Shopping_Cart` ADD FOREIGN KEY (`user_id`) REFERENCES `User` (`id`);

ALTER TABLE `Shopping_Cart` ADD FOREIGN KEY (`item_id`) REFERENCES `Item` (`id`);

ALTER TABLE `Order` ADD FOREIGN KEY (`user_id`) REFERENCES `User` (`id`);

ALTER TABLE `Order_Items` ADD FOREIGN KEY (`item_id`) REFERENCES `Item` (`id`);

ALTER TABLE `Order_Items` ADD FOREIGN KEY (`order_id`) REFERENCES `Order` (`id`);

ALTER TABLE `Comment` ADD FOREIGN KEY (`user_id`) REFERENCES `User` (`id`);

ALTER TABLE `Rating` ADD FOREIGN KEY (`user_id`) REFERENCES `User` (`id`);

ALTER TABLE `Rating` ADD FOREIGN KEY (`item_id`) REFERENCES `Item` (`id`);
