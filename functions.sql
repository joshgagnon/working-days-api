CREATE OR REPLACE FUNCTION array_intersect(anyarray, anyarray)
  RETURNS anyarray
  AS $$
        SELECT ARRAY(
            SELECT UNNEST($1)
            INTERSECT
            SELECT UNNEST($2)
        )
    $$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION stats(start_date date, end_date date)
    RETURNS TABLE(count bigint, flag text)
    AS $$
    SELECT count(flag) as count, flag
    FROM
        (SELECT day, jsonb_object_keys(flags) as flag FROM holidays WHERE day >= $1 AND day <= $2) q
    GROUP BY flag
    $$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION is_working_day(date, flags text[])
    RETURNS boolean
    AS $$
    SELECT EXISTS(SELECT 1 FROM holidays WHERE day = $1 and NOT (flags ?| $2) )
    $$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION holiday_range_json(start_date date, end_date date, flags text[])
    RETURNS JSON
    AS $$
    SELECT array_to_json(array_agg(row_to_json(q)))
    FROM (
        SELECT day, array_intersect(ARRAY(SELECT jsonb_object_keys(h.flags)), $3) as flags
        FROM holidays h WHERE day >= $1 AND day <= $2
        ) q
    WHERE array_length(q.flags, 1) > 0
    $$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION stats_json(start_date date, end_date date, flags text[])
    RETURNS JSON
    AS $$
    SELECT array_to_json(array_agg(row_to_json(q)))
    FROM
        (SELECT * FROM stats($1, $2) s WHERE s.flag = ANY($3)) q
    $$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION day_offset(start date, interval, flags text[], forward boolean, end_on_day boolean)
    RETURNS JSON
    AS $$
    SELECT json_build_object('result', day,
                             'stats', (CASE forward WHEN true THEN stats_json($1, day, $3) ELSE stats_json(day, $1, $3) END),
                             'range', (CASE forward WHEN true THEN holiday_range_json($1, day, $3) ELSE holiday_range_json(day, $1, $3) END)
                             )
    FROM (
        SELECT day FROM holidays
            WHERE ((forward and day >= (start + $2)) or (not forward and day <= start - $2)) AND ((end_on_day = true OR NOT (flags ?| $3)) or start = day)
            ORDER BY CASE forward WHEN true THEN day END asc, CASE forward WHEN false THEN day END desc
            LIMIT 1 ) q
    $$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION day_offset_round_down(start date, interval, flags text[], forward boolean, end_on_day boolean)
    RETURNS JSON
    AS $$
    SELECT CASE WHEN (day > $1 AND $4) OR (day <= $1 AND NOT $4) THEN json_build_object('result', day,
                             'stats', (CASE forward WHEN true THEN stats_json($1, day, $3) ELSE stats_json(day, $1, $3) END),
                             'range', (CASE forward WHEN true THEN holiday_range_json($1, day, $3) ELSE holiday_range_json(day, $1, $3) END)
                             )
                WHEN (day <= $1 AND $4) OR (day > $1 AND NOT $4) THEN day_offset($1, $2, $3, $4, $5)
                END

    FROM (
        SELECT day FROM holidays
            WHERE ((forward and day <= (start + $2)) or (not forward and day <= start - $2)) AND ((end_on_day = true OR NOT (flags ?| $3)) or start = day)
            ORDER BY day desc
            LIMIT 1 ) q
    $$ LANGUAGE SQL;



CREATE OR REPLACE FUNCTION working_day_offset(start date, count integer, flags text[], forward boolean default true)
    RETURNS JSON
    AS $$
    SELECT json_build_object('result', day,
                             'stats', (CASE forward WHEN true THEN stats_json($1, day, $3) ELSE stats_json(day, $1, $3) END),
                             'range', (CASE forward WHEN true THEN holiday_range_json($1, day, $3) ELSE holiday_range_json(day, $1, $3) END)
                             )
    FROM (
        SELECT day FROM holidays
            WHERE ((forward and day >= start) or (not forward and day <= start)) AND (NOT (flags ?| $3) or start = day)
            ORDER BY CASE forward WHEN true THEN day END asc, CASE forward WHEN false THEN day END desc
            OFFSET count
            LIMIT 1 ) q
    $$ LANGUAGE SQL;



CREATE OR REPLACE FUNCTION get_holidays()
    RETURNS JSON
    AS $$
    SELECT array_to_json(array_agg(row_to_json(q))) as holidays
    FROM
    (SELECT * from holidays where day >= (now() - interval '10 years') and day <= (now() + interval '10 years') AND flags<>'{}'::JSONB) q
    $$ LANGUAGE SQL;

