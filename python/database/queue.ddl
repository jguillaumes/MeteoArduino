CREATE TABLE queue (
    id integer primary key,
    data VARCHAR(128),
    isES smallint,
    isDB smallint
);

CREATE INDEX idx_es ON queue (isES, id);
CREATE INDEX idx_db ON queue (isDB, id);

