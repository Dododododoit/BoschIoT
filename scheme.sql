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

CREATE TABLE DeviceStatus (
  deviceID VARCHAR(20) NOT NULL,
  deviceType VARCHAR(20) DEFAULT NULL,
  Curtain INTEGER DEFAULT 0,
  Fans INTEGER DEFAULT 0,
  LED INTEGER DEFAULT 0
);

