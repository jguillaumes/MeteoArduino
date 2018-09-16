
CREATE SCHEMA WEATHER;
CREATE TABLE WEATHER.WEATHER (
    tsa bigint primary key, 
    time timestamp with time zone, 
    temperature real, 
    humidity real, 
    pressure real, 
    light real,
    fwVersion char(10),
    swVersion char(10),
    version char(10),
    isThermometer boolean,
    isBarometer boolean,
    isHygrometer boolean,
    isClock boolean
    );
CREATE INDEX WEATHER_TIME_IDX ON WEATHER.WEATHER(time desc);
COMMIT;
