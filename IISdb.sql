CREATE TABLE user(
    login varchar(64) NOT NULL PRIMARY KEY,
    first_name varchar(64) NOT NULL,
    last_name varchar(64) NOT NULL,
    password char(255) NOT NULL,
    email varchar(64) NOT NULL CONSTRAINT email_format_check CHECK (
    email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'
    ),
    IS_ADMIN int DEFAULT 0
);

CREATE TABLE device(
    id_device INT AUTO_INCREMENT PRIMARY KEY,
    description varchar(64) DEFAULT NULL,
    user_alias varchar(64) DEFAULT NULL,
    type varchar(64),

    login varchar(64),
    FOREIGN KEY (login) REFERENCES user(login)
);

CREATE TABLE parameter(
  id_param INT AUTO_INCREMENT PRIMARY KEY,
  name varchar(64),
  max_value INT,
  min_value INT
);

CREATE TABLE value(
    id_device INT,
    id_param INT,
    PRIMARY KEY(id_device, id_param),

    FOREIGN KEY (id_device) REFERENCES device(id_device),
    FOREIGN KEY (id_param) REFERENCES PARAMETER(id_param),

    current_value INT,
    KPI_THRESHOLD INT
);

CREATE TABLE systems(
    id_system INT AUTO_INCREMENT PRIMARY KEY,
    name varchar(64) NOT NULL,
    description varchar(64) DEFAULT NULL,

    login varchar(64),
    FOREIGN KEY (login) REFERENCES user(login)
);

CREATE TABLE users_systems(
    id_system INT,
    login varchar(64),
    PRIMARY KEY (login, id_system),
    FOREIGN KEY (id_system) REFERENCES systems(id_system),
    FOREIGN KEY (login) REFERENCES user(login)
);

CREATE TABLE device_systems(
    id_system INT,
    id_device INT,

    PRIMARY KEY (id_system),
    FOREIGN KEY (id_system) REFERENCES systems(id_system),
    FOREIGN KEY (id_device) REFERENCES device(id_device)
);



