CREATE DATABASE ewd_db;

\c ewd_db

-- Tạo bảng Dim_Book
CREATE TABLE Dim_Book (
    book_id INT PRIMARY KEY,
    bookname VARCHAR(255),
    genre VARCHAR(255),
    describe TEXT,
    pages_n INT,
    publish_date DATE,
    cover VARCHAR(255),
    price DECIMAL(10, 2)
);

-- Tạo bảng Dim_Author
CREATE TABLE Dim_Author (
    author_id INT PRIMARY KEY,
    author_name VARCHAR(255),
    total_books INT
);

-- Tạo bảng Dim_Date
CREATE TABLE Dim_Date (
    date_id SERIAL PRIMARY KEY,
    full_date DATE,
    year INT,
    month INT,
    day INT
);

-- Tạo bảng Fact_BookSales
CREATE TABLE Fact_BookSales (
    sales_id SERIAL PRIMARY KEY,
    book_id INT,
    date_id INT,
    author_id INT,
    quantity_sold INT,
    revenue DECIMAL(10, 2),
    rating DECIMAL(5, 2),
    FOREIGN KEY (book_id) REFERENCES Dim_Book(book_id),
    FOREIGN KEY (date_id) REFERENCES Dim_Date(date_id),
    FOREIGN KEY (author_id) REFERENCES Dim_Author(author_id)
);
