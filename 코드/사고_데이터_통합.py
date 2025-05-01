import pandas as pd

# [1] CSV 로드
csv_path = "데이터셋/서울_기상상태별교통사고.csv"
df = pd.read_csv(csv_path, encoding='utf-8-sig')

# [2] 필요 행 필터링
accident_row = df[(df.iloc[:, 0] == "서울") & (df.iloc[:, 1] == "사고[건]")].reset_index(drop=True)
death_row    = df[(df.iloc[:, 0] == "서울") & (df.iloc[:, 1] == "사망[명]")].reset_index(drop=True)
injury_row   = df[(df.iloc[:, 0] == "서울") & (df.iloc[:, 1] == "부상[명]")].reset_index(drop=True)

# [3] 숫자 변환 함수 정의
def extract_numeric_row(row):
    return row.iloc[0, 2:].astype(str).str.replace(",", "").astype(float)

try:
    # [4] 총합 및 눈 상태 사고 계산
    accident_values = extract_numeric_row(accident_row)
    snow_indices = list(range(8, len(accident_values), 7))  # 매 7번째가 '눈' 조건
    snow_accidents = accident_values.iloc[snow_indices].sum()
    total_accidents = accident_values.sum()
    snow_ratio = snow_accidents / total_accidents if total_accidents > 0 else 0

    # [5] 사고 심각도 계산
    total_deaths = extract_numeric_row(death_row).sum()
    total_injuries = extract_numeric_row(injury_row).sum()
    seriousness_score = 2 * total_deaths + total_injuries

    # [6] 출력
    print("📊 서울시 사고 통계 기반 지표:")
    print(f"- ❄️ 눈 상태 사고 비율: {snow_ratio:.2%}")
    print(f"- 🧊 겨울철 사고 건수 (전체 사고수로 대체): {total_accidents:,.0f}건")
    print(f"- ☠️ 사고 심각도 점수: {seriousness_score:,.0f}")

except Exception as e:
    print("🚨 오류 발생:", e)


road_df = pd.read_csv("광진구_도로_기상_통합.csv")

# [2] 새 컬럼 추가
road_df["snow_accident_ratio"] = snow_ratio
road_df["winter_accident_count"] = total_accidents
road_df["seriousness_score"] = seriousness_score

# [3] 저장
road_df.to_csv("광진구_도로_기상_기상상태사고_통합.csv", index=False, encoding="utf-8-sig")

print("✅ 기상+사고 통합 완료!")

# [1] 시간대별 사고 데이터 불러오기
df = pd.read_csv("데이터셋/서울_시간대별사고데이터.csv", encoding='utf-8-sig')

# [2] 사고[건] 행 필터링
accident_row = df[(df.iloc[:, 0] == "합계") & (df.iloc[:, 1] == "사고[건]")].reset_index(drop=True)

# [3] 새벽(0~9시) 열만 추출
# 컬럼명 예시: ['0~2시', '2~4시', '4~6시', '6~8시', '8~10시', ...]
early_cols = [col for col in accident_row.columns if any(t in col for t in ["0~", "2~", "4~", "6~", "8~"])]

# [4] 숫자형 변환
accident_data = accident_row.iloc[0, 2:]  # 앞 두 열 제외
accident_data = accident_data.astype(str).str.replace(",", "").astype(int)

# [5] 새벽 사고 비율 계산
total_accidents = accident_data.sum()
early_accidents = accident_data[early_cols].sum()
early_ratio = round(early_accidents / total_accidents, 4)

# [6] 도로 통합 파일 불러오기 및 병합
road_df = pd.read_csv("광진구_도로_기상_기상노면상태사고_통합.csv", encoding="utf-8-sig")
road_df["early_morning_accident_ratio"] = early_ratio

# [7] 저장
road_df.to_csv("광진구_도로_기상_기상노면상태_시간별사고_통합.csv", index=False, encoding="utf-8-sig")

# [8] 출력
print("📊 시간대별 사고 분석:")
print(f"- 총 사고 건수: {total_accidents:,}")
print(f"- 새벽 시간대 사고 건수: {early_accidents:,}")
print(f"- 🌙 새벽 사고 비율: {early_ratio:.2%}")

import pandas as pd

# [1] 시간대별 사고 데이터 불러오기
time_csv = "데이터셋/서울_시간대별사고데이터.csv"  # ← 네가 경로 수정
df = pd.read_csv(time_csv, encoding='utf-8-sig')

# [2] 사고[건] 데이터만 추출
accident_row = df[(df['사고년도'] == '사고[건]')].reset_index(drop=True)
print(accident_row)
if accident_row.empty:
    raise ValueError("🚨 '합계' + '사고[건]' 행이 없습니다. 데이터 확인하세요.")

# [3] 시간대별 사고 건수 가져오기
accident_values = accident_row.iloc[0, 3:].astype(str).str.replace(",", "").astype(float)

# [4] 전체 사고 수 계산
total_accidents = accident_values.sum()

# [5] 시간대 구간별 인덱스 계산
# 컬럼 순서: 00-02 / 02-04 / 04-06 / 06-08 / 08-10 / ... 22-24
# 즉, 0~4 인덱스가 00~10시 (새벽)
# 3~5 인덱스가 6~10시 (출근시간)
# 10,11 인덱스가 20-24시 (야간)

early_morning_indices = list(range(0, 5))  # 00시~10시
commute_peak_indices = [3, 4]              # 06시-08시 + 08시-10시
nighttime_indices = [10, 11]               # 20시-22시 + 22시-24시

# [6] 구간별 사고 수
early_morning_accidents = accident_values.iloc[early_morning_indices].sum()
commute_peak_accidents = accident_values.iloc[commute_peak_indices].sum()
nighttime_accidents = accident_values.iloc[nighttime_indices].sum()

# [7] 비율 계산
early_morning_ratio = early_morning_accidents / total_accidents if total_accidents > 0 else 0
commute_peak_ratio = commute_peak_accidents / total_accidents if total_accidents > 0 else 0
nighttime_ratio = nighttime_accidents / total_accidents if total_accidents > 0 else 0

# [8] 결과 출력
print(f"🌅 새벽 사고 비율: {early_morning_ratio:.2%}")
print(f"🚗 출근시간 사고 비율: {commute_peak_ratio:.2%}")
print(f"🌙 야간 사고 비율: {nighttime_ratio:.2%}")

# [9] 기존 도로 데이터에 병합
road_df = pd.read_csv("광진구_도로_기상_기상노면상태사고_통합.csv")  # ← 네가 경로 수정

road_df["early_morning_accident_ratio"] = early_morning_ratio
road_df["commute_peak_accident_ratio"] = commute_peak_ratio
road_df["nighttime_accident_ratio"] = nighttime_ratio

# [10] 저장
road_df.to_csv("광진구_도로_기상_기상노면상태_시간대사고_통합.csv", index=False, encoding="utf-8-sig")
print("✅ 시간대 사고 통합 완료!")

import pandas as pd

# [1] CSV 불러오기 (헤더 없음)
df = pd.read_csv("데이터셋/서울_사고유형별데이터.csv", encoding='utf-8-sig', header=None)

# [2] 각 행 위치 찾기
death_row = df[df.iloc[:, 2] == "사망[명]"].reset_index(drop=True)
injury_row = df[df.iloc[:, 2] == "부상[명]"].reset_index(drop=True)


## [3] 수치 전처리
def parse_values(row):
    return row.iloc[0, 3:].astype(str).str.replace(",", "").replace("-", "0").astype(float)

death_vals = parse_values(death_row)
injury_vals = parse_values(injury_row)

# [4] 결빙 유사 사고 유형 인덱스 (각 연도당 13개 그룹)
ice_type_offsets = [6, 7, 9, 10, 11]  # 추돌, 기타, 도로이탈, 전도전복, 기타
all_indices = []
for base in range(3, 3 + 13 * 4, 13):  # 2020~2023
    all_indices.extend([base + offset for offset in ice_type_offsets])

# [5] 결빙 관련 사망자/부상자 수
ice_deaths = death_vals.iloc[[i - 3 for i in all_indices]].sum()
ice_injuries = injury_vals.iloc[[i - 3 for i in all_indices]].sum()
print(ice_deaths)
print(ice_injuries)
# [6] 심각도 점수 계산
ice_severity_score = int(ice_deaths * 3 + ice_injuries)

# [7] 출력
print("📊 결빙 관련 사고 심각도 분석:")
print(f"- 사망자 수 (결빙 관련): {ice_deaths:.0f}명")
print(f"- 부상자 수 (결빙 관련): {ice_injuries:.0f}명")
print(f"- ☠️ 결빙 심각도 점수: {ice_severity_score:,}")

# [8] 병합 및 저장
road_df = pd.read_csv("광진구_도로_기상_기상노면상태_시간대사고_통합.csv", encoding="utf-8-sig")
road_df["ice_related_severity_score"] = ice_severity_score
road_df.to_csv("광진구_도로_기상_사고_데이터통합.csv", index=False, encoding="utf-8-sig")
print("✅ 심각도 점수 병합 완료!")