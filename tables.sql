DROP TABLE IF EXISTS holidays;
CREATE TABLE holidays (day date, flags jsonb, summary_flags jsonb);
CREATE INDEX ON holidays(day);
CREATE INDEX idxgin ON holidays USING gin (summary_flags);



CREATE OR REPLACE FUNCTION working_days(start date, count integer, flags text[])
    RETURNS date
    AS $$
        SELECT day FROM holidays
            WHERE day >= start AND NOT (summary_flags ?| $3)
            ORDER BY day
            OFFSET count
            LIMIT 1
    $$ LANGUAGE SQL;
