DROP TABLE IF EXISTS holidays;
CREATE TABLE holidays (day date, flags jsonb, summary_flags jsonb);
CREATE INDEX ON holidays(day);
CREATE INDEX idxgin ON holidays USING gin (summary_flags);


