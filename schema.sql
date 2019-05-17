DROP TABLE IF EXISTS blog_posts;
DROP TABLE IF EXISTS authors;


CREATE TABLE authors (
  author_id INTEGER PRIMARY KEY AUTOINCREMENT,
  firstname TEXT NOT NULL,
  lastname TEXT NOT NULL,
  email TEXT NOT NULL,
  password TEXT NOT NULL
);


CREATE TABLE blog_posts (
  post_id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  post_content TEXT,
  date TEXT NOT NULL,
  author_id INTEGER NOT NULL,
  FOREIGN KEY (author_id) REFERENCES authors(author_id)
);