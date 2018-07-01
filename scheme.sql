CREATE TABLE temperature (
  deviceID VARCHAR(20) NOT NULL,
  temperatureValue FLOAT DEFAULT NULL,
  ctime TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE carbonDioxide (
  deviceID VARCHAR(20) NOT NULL,
  CO2value FLOAT DEFAULT NULL,
  ctime TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE light (
  deviceID VARCHAR(20) NOT NULL,
  lightValue INTEGER DEFAULT NULL,
  ctime TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE humidity (
  deviceID VARCHAR(20) NOT NULL,
  humidityValue FLOAT DEFAULT NULL,
  ctime TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);

