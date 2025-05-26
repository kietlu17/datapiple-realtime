-- Tạo bảng dim_author

CREATE TABLE Author (
    author_id INT PRIMARY KEY,
    author VARCHAR(255)
);

CREATE TABLE Rating (
    book_id INT PRIMARY KEY,
    rating  DECIMAL(5, 2),
    fivestars INT,
    fourstars INT,
    threestars INT,
    twostars INT,
    onestar INT
);


-- Tạo bảng book
CREATE TABLE Book (
    book_id INT PRIMARY KEY,
    author_id INT,
    rating  DECIMAL(5, 2),
    genre VARCHAR(255),
    describe TEXT,
    author VARCHAR(255),
    bookname VARCHAR(255),
    publish Date,
    prices  DECIMAL(5, 2),
    ratingcount INT,
    quantity  INT,
    pages_n INT,
    cover VARCHAR(255),
    FOREIGN KEY (book_id) REFERENCES Rating(book_id),
    FOREIGN KEY (author_id) REFERENCES Author(author_id)
);



CREATE TABLE Describe (
    book_id INT,
    author_id INT,
    describe TEXT,
    bookUrl VARCHAR(255),
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES Book(book_id),
    FOREIGN KEY (author_id) REFERENCES Author(author_id)
);



