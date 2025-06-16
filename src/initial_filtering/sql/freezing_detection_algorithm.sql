create database doitsql;
Use doitsql;

CREATE TABLE surface_temperature (
    timestamp BIGINT,    -- CSV의 timestamp가 숫자 형태이므로 BIGINT 사용 (필요시 DATETIME으로 변환)
    ts_avg DOUBLE
);

CREATE TABLE weather_230101 (
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
    -- 현재 행 기준 이전 값들 (weather_230101.timestamp 기준 오름차순 정렬)
    LAG(surface_temperature.ts_avg, 1) OVER (ORDER BY weather_230101.timestamp) AS prev_ts_avg,
    LAG(weather_230101.rn_60m, 3) OVER (ORDER BY weather_230101.timestamp) AS rn_60m_3,
    LAG(weather_230101.ta, 1) OVER (ORDER BY weather_230101.timestamp) AS ta_prev1,
    LAG(weather_230101.ta, 2) OVER (ORDER BY weather_230101.timestamp) AS ta_prev2,
    LAG(weather_230101.ta, 3) OVER (ORDER BY weather_230101.timestamp) AS ta_prev3
  FROM weather_230101
  JOIN surface_temperature 
    ON weather_230101.timestamp = surface_temperature.timestamp
  WHERE weather_230101.lon = 127.0895589
    AND weather_230101.lat = 37.55989126
),
conds AS (
  SELECT
    *,
    -- 알고리즘 조건 1: hm >= 65, ts_avg <= td+5, ta <= 5, ts_avg <= 0
    (
      (hm >= 65)
      AND (ts_avg <= td + 5)
      AND (ta <= 5)
      AND (ts_avg <= 0)
    ) AS cond1,
    
    -- 알고리즘 조건 2: hm >= 65, ts_avg <= td+5, ta <= 5, 0 < ts_avg <= 1, 그리고 이전 ts_avg와 비교 시 차이가 >= 1
    (
      (hm >= 65)
      AND (ts_avg <= td + 5)
      AND (ta <= 5)
      AND (ts_avg > 0 AND ts_avg <= 1)
      AND (prev_ts_avg IS NOT NULL AND (prev_ts_avg - ts_avg) <= -1)
    ) AS cond2,
    
    -- 알고리즘 조건 3: 3번째 전 rn_60m > 1, ts_avg <= 0, 그리고 (3번째 전, 2번째 전, 1번째 전, 본 데이터 중) 하나라도 ta <= 0
    (
      (rn_60m_3 > 1)
      AND (ts_avg <= 0)
      AND ((ta_prev3 <= 0) OR (ta_prev2 <= 0) OR (ta_prev1 <= 0) OR (ta <= 0))
    ) AS cond3,
    
    -- 알고리즘 조건 4: sd_3hr가 0이 아님
    (sd_3hr <> 0) AS cond4,
    
    -- 알고리즘 조건 5: ts_avg <= 0, ABS(ts_avg - (td+5)) < 0.5, ws_10m > 2
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
    SUM(cond_flag) OVER (ORDER BY weather_timestamp ROWS BETWEEN 4 PRECEDING AND 1 PRECEDING) AS prev_cond_count
  FROM with_flag
)
SELECT COUNT(*) AS total_count
FROM with_prev
WHERE 
  (
    cond1 OR cond2 OR cond3 OR cond4 OR cond5
    OR (
         -- 알고리즘 조건 6: ta <= 0, ts_avg <= 0, 그리고 이전 4행 중 조건1~5를 만족하는 행이 하나 이상 존재
         (ta <= 0)
         AND (ts_avg <= 0)
         AND (prev_cond_count > 0)
       )
  );
  
  -- Count 구문 사용 안 하고 어떤 게 선택되었는지 확인 하는 구문
  WITH base AS (
  SELECT
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
    -- 현재 행 기준 이전 값들 (weather_230101.timestamp 기준 오름차순 정렬)
    LAG(surface_temperature.ts_avg, 1) OVER (ORDER BY weather_230101.timestamp) AS prev_ts_avg,
    LAG(weather_230101.rn_60m, 3) OVER (ORDER BY weather_230101.timestamp) AS rn_60m_3,
    LAG(weather_230101.ta, 1) OVER (ORDER BY weather_230101.timestamp) AS ta_prev1,
    LAG(weather_230101.ta, 2) OVER (ORDER BY weather_230101.timestamp) AS ta_prev2,
    LAG(weather_230101.ta, 3) OVER (ORDER BY weather_230101.timestamp) AS ta_prev3
  FROM weather_230101
  JOIN surface_temperature 
    ON weather_230101.timestamp = surface_temperature.timestamp
  WHERE weather_230101.lon = 127.0895589
    AND weather_230101.lat = 37.55989126
),
conds AS (
  SELECT
    *,
    -- 알고리즘 조건 1: hm >= 65, ts_avg <= td+5, ta <= 5, ts_avg <= 0
    (
      (hm >= 65)
      AND (ts_avg <= td + 5)
      AND (ta <= 5)
      AND (ts_avg <= 0)
    ) AS cond1,
    
    -- 알고리즘 조건 2: hm >= 65, ts_avg <= td+5, ta <= 5, 0 < ts_avg <= 1, 그리고 이전 ts_avg와 비교 시 차이가 >= 1
    (
      (hm >= 65)
      AND (ts_avg <= td + 5)
      AND (ta <= 5)
      AND (ts_avg > 0 AND ts_avg <= 1)
      AND (prev_ts_avg IS NOT NULL AND (prev_ts_avg - ts_avg) <= -1)
    ) AS cond2,
    
    -- 알고리즘 조건 3: 3번째 전 rn_60m > 1, ts_avg <= 0, 그리고 (3번째 전, 2번째 전, 1번째 전, 본 데이터 중) 하나라도 ta <= 0
    (
      (rn_60m_3 > 1)
      AND (ts_avg <= 0)
      AND ((ta_prev3 <= 0) OR (ta_prev2 <= 0) OR (ta_prev1 <= 0) OR (ta <= 0))
    ) AS cond3,
    
    -- 알고리즘 조건 4: sd_3hr가 0이 아님
    (sd_3hr <> 0) AS cond4,
    
    -- 알고리즘 조건 5: ts_avg <= 0, ABS(ts_avg - (td+5)) < 0.5, ws_10m > 2
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
    SUM(cond_flag) OVER (ORDER BY weather_timestamp ROWS BETWEEN 4 PRECEDING AND 1 PRECEDING) AS prev_cond_count
  FROM with_flag
)
SELECT *
FROM with_prev
WHERE 
  ( cond1 OR cond2 OR cond3 OR cond4 OR cond5
    OR (
         -- 알고리즘 조건 6: ta <= 0, ts_avg <= 0, 그리고 이전 4행 중 조건 1~5 중 하나라도 만족하는 경우
         (ta <= 0)
         AND (ts_avg <= 0)
         AND (prev_cond_count > 0)
       )
  );

-- create_table.sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(100)
);
