-- 1. Create a table (SQLite doesn't need a CREATE DATABASE command, the file IS the database)
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    year INTEGER,
    genre TEXT,
    rating REAL
);

-- 2. Insert at least 8 books
INSERT INTO books (title, author, year, genre, rating) VALUES 
('The Martian', 'Andy Weir', 2011, 'Science Fiction', 4.8),
('1984', 'George Orwell', 1949, 'Fiction', 4.6),
('Dune', 'Frank Herbert', 1965, 'Science Fiction', 4.7),
('The Hunger Games', 'Suzanne Collins', 2008, 'Fiction', 4.3),
('Sapiens', 'Yuval Noah Harari', 2011, 'Non-Fiction', 4.5),
('To Kill a Mockingbird', 'Harper Lee', 1960, 'Fiction', 4.9),
('Project Hail Mary', 'Andy Weir', 2021, 'Science Fiction', 4.9),
('Atomic Habits', 'James Clear', 2018, 'Non-Fiction', 4.8);

-- 7. Print all query results neatly with labels
.mode column
.headers on

-- 3. Query 1: Books published after 2000, ordered by rating (highest first)
SELECT '--- Query 1: Post-2000 Books ---' AS Label;
SELECT title, year, rating FROM books WHERE year > 2000 ORDER BY rating DESC;

-- 4. Query 2: 'Fiction' genre with rating above 4.0
SELECT '--- Query 2: Fiction Books > 4.0 ---' AS Label;
SELECT title, author, rating FROM books WHERE genre = 'Fiction' AND rating > 4.0;

-- 5. Query 3: Find the average rating across all books
SELECT '--- Query 3: Average Rating ---' AS Label;
SELECT ROUND(AVG(rating), 2) AS Average_Rating FROM books;

-- 6. Query 4: Count per genre
SELECT '--- Query 4: Book Count Per Genre ---' AS Label;
SELECT genre, COUNT(*) AS Total FROM books GROUP BY genre;

-- Bonus: Add a reviews table
CREATE TABLE IF NOT EXISTS reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER,
    review_text TEXT,
    FOREIGN KEY (book_id) REFERENCES books(id)
);