import pandas as pd

# 1. 텍스트 파일 불러오기 (구분자: |, 컬럼 수 맞춰야 함)
col_names = [
    "OBJECT_ID", "X", "Y", "법정코드", "시도", "시군구", "읍면동", 
    "도로명코드", "도로명", "지하여부", "건물본번", "건물부번", 
    "법정동코드", "도로명주소여부", "비고1", "비고2"
]

df = pd.read_csv("./data/Total.JUSUAN.20250401.TI_SPOT_BUSST_ADRES.TXT", sep="|", names=col_names, dtype=str, encoding="euc-kr")

# 2. 광진구 데이터만 필터링
df_gwangjin = df[df["시군구"] == "광진구"]

# 3. 결과 저장
df_gwangjin.to_csv("광진구_도로명_주소마스터.csv", index=False)

print(f"✅ 필터링 완료! 총 {len(df_gwangjin)}건의 광진구 도로명 데이터가 저장되었습니다.")
