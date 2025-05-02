create database doitsql;
Use doitsql;

CREATE TABLE surface_temperature (
    timestamp BIGINT,    -- CSV의 timestamp가 숫자 형태이므로 BIGINT 사용 (필요시 DATETIME으로 변환)
    ts_avg DOUBLE
);

CREATE TABLE weather_230101 (
    gid DOUBLE,
    lon DOUBLE,
    lat DOUBLE,
    timestamp BIGINT,  -- '202301010000'과 같은 문자열 형태로 저장 (필요시 DATETIME으로 변환)
    ta DOUBLE,
    hm DOUBLE,
    td DOUBLE,
    ws_10m DOUBLE,
    rn_60m DOUBLE,
    sd_3hr DOUBLE
);

-- CSV 파일1 import
LOAD DATA INFILE '230101_weather.csv'
INTO TABLE weather_230101
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

-- CSV 파일2 import
LOAD DATA INFILE 'surface_temperature.csv'
INTO TABLE surface_temperature
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

WITH base AS (
  SELECT
    weather_230101.gid,
    weather_230101.lon,
    weather_230101.lat,
    weather_230101.timestamp AS weather_timestamp,
    weather_230101.ta,
    weather_230101.hm,
    weather_230101.td,
    weather_230101.ws_10m,
    weather_230101.rn_60m,
    weather_230101.sd_3hr,
    surface_temperature.ts_avg,
    LAG(surface_temperature.ts_avg, 1) OVER (ORDER BY weather_230101.timestamp) AS prev_ts_avg,
    LAG(weather_230101.rn_60m, 3) OVER (ORDER BY weather_230101.timestamp) AS rn_60m_3,
    LAG(weather_230101.ta, 1) OVER (ORDER BY weather_230101.timestamp) AS ta_prev1,
    LAG(weather_230101.ta, 2) OVER (ORDER BY weather_230101.timestamp) AS ta_prev2,
    LAG(weather_230101.ta, 3) OVER (ORDER BY weather_230101.timestamp) AS ta_prev3
  FROM weather_230101
  JOIN surface_temperature 
    ON weather_230101.timestamp = surface_temperature.timestamp
  -- 여기서 gid를 전체 범위(1~94)로 제한하거나 조건을 제거하세요.
  WHERE weather_230101.gid BETWEEN 1 AND 94
),
conds AS (
  SELECT
    *,
    ( (hm >= 65)
      AND (ts_avg <= td + 5)
      AND (ta <= 5)
      AND (ts_avg <= 0)
    ) AS cond1,
    (
      (hm >= 65)
      AND (ts_avg <= td + 5)
      AND (ta <= 5)
      AND (ts_avg > 0 AND ts_avg <= 1)
      AND (prev_ts_avg IS NOT NULL AND (prev_ts_avg - ts_avg) <= -1)
    ) AS cond2,
    (
      (rn_60m_3 > 1)
      AND (ts_avg <= 0)
      AND ((ta_prev3 <= 0) OR (ta_prev2 <= 0) OR (ta_prev1 <= 0) OR (ta <= 0))
    ) AS cond3,
    (sd_3hr <> 0) AS cond4,
    (
      (ts_avg <= 0)
      AND (ABS(ts_avg - (td + 5)) < 0.5)
      AND (ws_10m > 2)
    ) AS cond5
  FROM base
),
with_flag AS (
  SELECT
    *,
    CASE WHEN (cond1 OR cond2 OR cond3 OR cond4 OR cond5) THEN 1 ELSE 0 END AS cond_flag
  FROM conds
),
with_prev AS (
  SELECT
    *,
    SUM(cond_flag) OVER (PARTITION BY gid ORDER BY weather_timestamp ROWS BETWEEN 4 PRECEDING AND 1 PRECEDING) AS prev_cond_count
  FROM with_flag
)
-- 최종적으로 각 gid별로 조건에 해당하는 행 수를 구합니다.
SELECT gid, COUNT(*) AS total_count
FROM with_prev
WHERE 
  (
    cond1 OR cond2 OR cond3 OR cond4 OR cond5
    OR (
         (ta <= 0)
         AND (ts_avg <= 0)
         AND (prev_cond_count > 0)
       )
  )
GROUP BY gid;
