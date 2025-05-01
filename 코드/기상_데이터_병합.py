import pandas as pd

# [1] 데이터 불러오기
road_df = pd.read_csv("광진구_통합_1차.csv")
weather_df = pd.read_csv("광진구_최종_기후적설_통합.csv")

# [2] weather_df 평균값 계산 (NaN은 0으로 대체)
weather_df.fillna(0, inplace=True)

avg_temp = weather_df["평균기온"].mean()
avg_rainfall = weather_df["평균강수량"].mean()
avg_snowfall = weather_df["평균적설량"].mean()
early_morning_rain_peak_rate = weather_df["early_morning_rain_peak"].mean()
early_morning_snow_peak_rate = weather_df["early_morning_snow_peak"].mean()

# [3] road_df에 기상 평균값 추가
road_df["avg_temp"] = avg_temp
road_df["avg_rainfall"] = avg_rainfall
road_df["avg_snowfall"] = avg_snowfall
road_df["early_morning_rain_peak_rate"] = early_morning_rain_peak_rate
road_df["early_morning_snow_peak_rate"] = early_morning_snow_peak_rate

# [4] 최종 저장
output_path = "광진구_도로_기상_통합.csv"
road_df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"✅ 기상 데이터 통합 완료! 저장 경로: {output_path}")
