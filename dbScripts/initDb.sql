CREATE TABLE User (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3)
);

CREATE TABLE Post (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (user_id) REFERENCES User(id)
);

CREATE TABLE Category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(255) UNIQUE NOT NULL,
    decription TINYTEXT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3)
);

CREATE TABLE PostCategory (
    post_id INT,
    category_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (post_id) REFERENCES Post(id),
    FOREIGN KEY (category_id) REFERENCES Category(id),
    PRIMARY KEY (post_id, category_id)
);

CREATE TABLE Vendor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tech_name VARCHAR(255) UNIQUE NOT NULL,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3)
);

CREATE TABLE UserVendor (
    user_id INT,
    vendor_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (vendor_id) REFERENCES Vendor(id),
    PRIMARY KEY (user_id, vendor_id)
);

CREATE TABLE PostVendor (
    post_id INT,
    vendor_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (post_id) REFERENCES Post(id),
    FOREIGN KEY (vendor_id) REFERENCES Vendor(id),
    PRIMARY KEY (post_id, vendor_id)
);

CREATE TABLE Comment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT,
    user_id INT,
    comment_text TEXT NOT NULL,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (post_id) REFERENCES Post(id),
    FOREIGN KEY (user_id) REFERENCES User(id)
);

CREATE TABLE CommentTag (
    comment_id INT,
    tagged_user_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (comment_id) REFERENCES Comment(id),
    FOREIGN KEY (tagged_user_id) REFERENCES User(id),
    PRIMARY KEY (comment_id, tagged_user_id)
);

CREATE TABLE PostUpvote (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT,
    user_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (post_id) REFERENCES Post(id),
    FOREIGN KEY (user_id) REFERENCES User(id)
);

CREATE TABLE CommentUpvote (
    id INT AUTO_INCREMENT PRIMARY KEY,
    comment_id INT,
    user_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (comment_id) REFERENCES Comment(id),
    FOREIGN KEY (user_id) REFERENCES User(id)
);
