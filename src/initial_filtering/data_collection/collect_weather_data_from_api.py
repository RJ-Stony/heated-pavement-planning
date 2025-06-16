import pandas as pd
import requests
from datetime import datetime, timedelta
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import csv
import os

def fetch_api_data_by_coord(lon, lat, date_str, api_url, authKey, obs, itv, help_param, timeout=30, max_retries=5, backoff_factor=1.5):
    tm1 = f"{date_str}0000"
    tm2 = f"{date_str}2300"

    params = {
        "tm1": tm1,
        "tm2": tm2,
        "lon": lon,
        "lat": lat,
        "obs": obs,
        "itv": itv,
        "help": help_param,
        "authKey": authKey
    }

    for attempt in range(1, max_retries + 1):
        try:
            print(f"호출 시도 ({attempt}/{max_retries}): {lon}, {lat}, {date_str}")
            response = requests.get(api_url, params=params, timeout=timeout)
            if response.status_code == 200:
                response_text = response.text
                if "#START7777" in response_text and "#7777END" in response_text:
                    return {"lon": lon, "lat": lat, "date": date_str, "response": response_text, "status": "success"}
                elif len(response_text.strip().split("\n")) > 1:
                    return {"lon": lon, "lat": lat, "date": date_str, "response": response_text, "status": "success"}
                else:
                    result = f"Insufficient data: {response_text[:50]}..."
            else:
                result = f"Error: {response.status_code}"
        except requests.exceptions.Timeout:
            result = f"Timeout (attempt {attempt}/{max_retries})"
        except Exception as e:
            result = f"Exception: {str(e)}"

        wait_time = backoff_factor ** attempt
        print(f"재시도 대기 중 ({wait_time:.1f}초): {lon}, {lat}, {date_str}")
        time.sleep(wait_time)

    return {"lon": lon, "lat": lat, "date": date_str, "response": result, "status": "failed"}

def generate_date_range(start_date_str, end_date_str):
    start = datetime.strptime(start_date_str, "%Y%m%d")
    end = datetime.strptime(end_date_str, "%Y%m%d")
    return [(start + timedelta(days=i)).strftime("%Y%m%d") for i in range((end - start).days + 1)]

def parse_api_response(response_text):
    if "#START7777" in response_text and "#7777END" in response_text:
        start_idx = response_text.find("#START7777") + len("#START7777")
        end_idx = response_text.find("#7777END")
        return response_text[start_idx:end_idx].strip()
    return response_text.strip()

def main():
    df_coords = pd.read_csv("500m_grid_centroids.csv")
    print(f"총 {len(df_coords)} 개의 좌표 로드 완료")

    api_url = "https://apihub.kma.go.kr/api/typ01/url/sfc_nc_var.php"
    authKey = "myauthKey"
    obs = "ta,hm,td,ws_10m,rn_60m,sd_3hr"
    itv = "60"
    help_param = "0"

    # 2023년 1월 데이터만 예시
    date_list = generate_date_range("20230101", "20230131")
    max_workers = 10
    all_results = []

    for date_str in date_list:
        print(f"\n==== {date_str} 데이터 요청 시작 ====")
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_coord = {
                executor.submit(
                    fetch_api_data_by_coord,
                    str(row["lon"]), str(row["lat"]),
                    date_str,
                    api_url, authKey, obs, itv, help_param
                ): (row["lon"], row["lat"]) for _, row in df_coords.iterrows()
            }

            for future in tqdm(as_completed(future_to_coord), total=len(future_to_coord), desc=f"{date_str}"):
                result = future.result()
                results.append(result)

        daily_df = pd.DataFrame(results)
        daily_df.to_csv(f"api_results_{date_str}.csv", index=False)
        all_results.extend(results)
        print(f"{date_str} 결과 저장 완료")

    final_df = pd.DataFrame(all_results)
    final_df.to_csv("api_results_by_coordinates.csv", index=False)

    print("\n모든 날짜의 데이터 수집이 완료되었습니다.")

    # 추가: 파싱하여 하나의 통합 파일로 저장
    output_parsed_file = "parsed_weather_data_all_days.csv"
    with open(output_parsed_file, "w", newline="") as csvfile:
        fieldnames = ["lon", "lat", "date", "timestamp", "ta", "hm", "td", "ws_10m", "rn_60m", "sd_3hr"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for result in all_results:
            if result["status"] != "success":
                continue

            lon, lat, date, response_text = result["lon"], result["lat"], result["date"], result["response"]
            cleaned_text = parse_api_response(response_text)
            for line in cleaned_text.split("\n"):
                parts = [p.strip() for p in line.strip().split(",")]
                if len(parts) >= 7:
                    writer.writerow({
                        "lon": lon,
                        "lat": lat,
                        "date": date,
                        "timestamp": parts[0],
                        "ta": parts[1],
                        "hm": parts[2],
                        "td": parts[3],
                        "ws_10m": parts[4],
                        "rn_60m": parts[5],
                        "sd_3hr": parts[6]
                    })

    print(f"\n통합된 파싱 결과가 '{output_parsed_file}'에 저장되었습니다.")

if __name__ == '__main__':
    main()
