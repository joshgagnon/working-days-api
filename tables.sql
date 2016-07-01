DROP TABLE IF EXISTS holidays;
CREATE TABLE holidays (day date, flags jsonb);
CREATE INDEX ON holidays(day);
CREATE INDEX idxgin ON holidays USING gin (flags);


