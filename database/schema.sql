CREATE DATABASE food_delivery;
USE food_delivery;

CREATE TABLE Users (

);

CREATE TABLE Restaurants (

);

CREATE TABLE Orders (

);

CREATE TABLE Food (

);

CREATE TABLE Couriers (
    courier_id INT PRIMARY KEY,
    name VARCHAR(255),
    gender VARCHAR(50),
    birth_date DATE,
    restaurant_id INT,
    FOREIGN KEY (restaurant_id) REFERENCES Restaurants(restaurant_id)
);

CREATE TABLE Menu (

);