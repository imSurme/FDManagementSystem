CREATE DATABASE food_delivery;
USE food_delivery;

CREATE TABLE admins (
    admin_id INT AUTO_INCREMENT,
    email VARCHAR(150) NOT NULL,
    password VARCHAR(255) NOT NULL,
    PRIMARY KEY (admin_id)
);

CREATE TABLE users (
    user_id INT AUTO_INCREMENT,
    name VARCHAR(30) NOT NULL,
    email VARCHAR(50) NOT NULL,
    password VARCHAR(20) NOT NULL,
    age INT NOT NULL CHECK(age >= 12),
    gender VARCHAR(15) NOT NULL,
    marital_status VARCHAR(30) NOT NULL,
    occupation VARCHAR(30) NOT NULL,
    monthly_income VARCHAR(30) NOT NULL,
    educational_qualifications VARCHAR(30) NOT NULL,
    family_size INT NOT NULL CHECK(family_size >= 0),
    PRIMARY KEY (user_id)
);

CREATE TABLE restaurants (
    restaurant_id INT AUTO_INCREMENT,
    user_id INT NOT NULL,
    restaurant_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    rating DECIMAL(2,1),
    rating_count VARCHAR(50),
    average_cost INT NOT NULL CHECK(average_cost >= 0),
    cuisine VARCHAR(100) NOT NULL,
    restaurant_address TEXT NOT NULL,
    PRIMARY KEY (restaurant_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE orders (
    order_id INT AUTO_INCREMENT,
    order_date DATE NOT NULL,
    sales_qty FLOAT NOT NULL,
    sales_amount FLOAT NOT NULL,
    user_id INT NOT NULL,
    restaurant_id INT NOT NULL,
    order_status VARCHAR(20) NOT NULL,
    PRIMARY KEY (order_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
);

CREATE TABLE food (
    food_id INT AUTO_INCREMENT,
    item_name VARCHAR(255) NOT NULL,
    veg_or_non_veg ENUM('Veg', 'Non-veg') NOT NULL,
    PRIMARY KEY (food_id)
);

CREATE TABLE couriers (
    courier_id INT AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    gender ENUM('Male', 'Female') NOT NULL,
    birth_date DATE NOT NULL,
    restaurant_id INT,
    PRIMARY KEY (courier_id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);


CREATE TABLE menu (
    menu_id INT AUTO_INCREMENT,
    restaurant_id INT NOT NULL,
    food_id INT NOT NULL,
    cuisine VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL CHECK(price >= 0),
    PRIMARY KEY (menu_id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id),
    FOREIGN KEY (food_id) REFERENCES food(food_id)
);
