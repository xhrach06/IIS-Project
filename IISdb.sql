CREATE TABLE user(
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name varchar(64) NOT NULL,
    last_name varchar(64) NOT NULL,
    password varchar(64) NOT NULL,
    email varchar(64) NOT NULL UNIQUE CONSTRAINT email_format_check CHECK (
    email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'
    ),
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_admin INT DEFAULT 0,
    is_broker INT DEFAULT 0
);

CREATE TABLE device(
    device_id INT AUTO_INCREMENT PRIMARY KEY,
    name varchar(64) NOT NULL,
    description varchar(256) DEFAULT NULL,
    
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);

CREATE TABLE parameter(
  param_id INT AUTO_INCREMENT PRIMARY KEY,
  name varchar(64),
  max_value INT NOT NULL,
  min_value INT NOT NULL,
  kpi_on_off INT DEFAULT 0, -- 0=off, 1=on
  ok_if INT DEFAULT NULL, -- 0=lower, 1=higher
  kpi_treshold DEFAULT NULL,
  current_value INT 

  device_id INT,
  FOREIGN KEY (device_id) REFERENCES device(device_id) ON DELETE CASCADE
);

--This trigger automatically sets current_value to the value of min_value for each new row inserted into the table.
CREATE TRIGGER set_current_value
BEFORE INSERT ON parameter
FOR EACH ROW
SET NEW.current_value = NEW.min_value;


CREATE TABLE systems(
    system_id INT AUTO_INCREMENT PRIMARY KEY,
    name varchar(64) NOT NULL,
    description varchar(256) DEFAULT NULL,

    user_id INT,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);

CREATE TABLE users_systems(
    system_id INT,
    user_id INT, 
    shared_since DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, system_id),
    FOREIGN KEY (system_id) REFERENCES system(system_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);

CREATE TABLE device_systems(
    system_id INT,
    device_id INT,

    PRIMARY KEY (system_id, device_id),
    FOREIGN KEY (system_id) REFERENCES systems(system_id) ON DELETE CASCADE,
    FOREIGN KEY (device_id) REFERENCES device(device_id) ON DELETE CASCADE
);



