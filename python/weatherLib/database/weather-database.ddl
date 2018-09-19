
CREATE SCHEMA WEATHER;
CREATE TABLE WEATHER.WEATHER (
    tsa bigint primary key, 
    time timestamp with time zone not null, 
    temperature real, 
    humidity real, 
    pressure real, 
    light real,
    fwVersion char(10) not null,
    swVersion char(10) not null,
    version char(10) not null,
    isThermometer boolean default 't',
    isBarometer boolean default 't',
    isHygrometer boolean default 't',
    isClock boolean default 't',
    esDocId varchar(32) not null
    );
CREATE INDEX WEATHER_TIME_IDX ON WEATHER.WEATHER(time desc);
create unique index weather_esdocid_idx on weather.weather(esDocId);

COMMIT;
