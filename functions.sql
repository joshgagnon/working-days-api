CREATE OR REPLACE FUNCTION working_days(start date, count integer, flags text[])
    RETURNS date
    AS $$
        SELECT day FROM holidays
            WHERE day >= start AND NOT (summary_flags ?| $3)
            ORDER BY day
            OFFSET count
            LIMIT 1
    $$ LANGUAGE SQL;
