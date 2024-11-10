CREATE DATABASE food_delivery;
USE food_delivery;

CREATE TABLE Users (

);

CREATE TABLE Restaurants (
    restaurant_id INT AUTO_INCREMENT,
    user_id INT NOT NULL,
    restaurant_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    rating DECIMAL(2,1),
    rating_count VARCHAR(50),
    average_cost INT CHECK(average_cost >= 0),
    cuisine VARCHAR(100) NOT NULL,
    restaurant_address TEXT NOT NULL,
    PRIMARY KEY (restaurant_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Orders (

);

CREATE TABLE Food (
    food_id INT AUTO_INCREMENT,
    item_name VARCHAR(100) NOT NULL,
    veg_or_non_veg ENUM('Veg', 'Non-veg') NOT NULL,
    PRIMARY KEY (food_id)
);

CREATE TABLE Couriers (

);


CREATE TABLE Menu (

);
