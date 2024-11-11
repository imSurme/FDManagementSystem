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
    average_cost INT NOT NULL CHECK(average_cost >= 0),
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
    courier_id INT AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    gender VARCHAR(50) NOT NULL,
    birth_date DATE NOT NULL,
    restaurant_id INT NOT NULL,
    PRIMARY KEY (courier_id),
    FOREIGN KEY (restaurant_id) REFERENCES Restaurants(restaurant_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);


CREATE TABLE Menu (
    menu_id INT AUTO_INCREMENT,
    restaurant_id INT NOT NULL,
    food_id INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL CHECK(price >= 0),
    PRIMARY KEY (menu_id),
    FOREIGN KEY (restaurant_id) REFERENCES Restaurants(restaurant_id),
    FOREIGN KEY (food_id) REFERENCES Food(food_id)
);
