import pandas as pd
import numpy as np
import folium
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# ✅ 한글 깨짐 방지 설정 (Windows 기준)
plt.rcParams['font.family'] = 'Malgun Gothic'  # mac이면 'AppleGothic', Ubuntu면 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

# 1. 데이터 로드
df = pd.read_csv("광진구_최종_데이터통합_.csv")
freeze_df = pd.read_csv("행정안전부_상습 결빙구간_광진구.txt", delimiter=",", encoding="utf-8")

# 2. 기본 식별 칼럼
id_cols = ["도로명", "전체주소", "위도", "경도"]

# 3. 위험요소 엔지니어링
equip_cols = ["열선설치여부", "제설함여부", "염화칼슘여부", "모래주머니여부"]
df["equipment_deficit"] = df[equip_cols].apply(lambda row: (1 - row).sum(), axis=1)

# 기온 위험
if "avg_temp" in df.columns:
    max_temp = df["avg_temp"].max()
    df["temp_risk"] = max_temp - df["avg_temp"]
else:
    df["temp_risk"] = np.nan

# 사고 관련 합산
accident_cols = ["snow_accident_ratio", "winter_accident_count", "seriousness_score",
                 "icy_surface_accident_ratio", "early_morning_accident_ratio",
                 "commute_peak_accident_ratio", "nighttime_accident_ratio", "ice_related_severity_score"]
accident_cols = [col for col in accident_cols if col in df.columns]
df["accident_sum"] = df[accident_cols].sum(axis=1)

# 위험 요소 칼럼
risk_factors = ["경사도(%)", "equipment_deficit", "temp_risk", 
                "avg_rainfall", "avg_snowfall", "accident_sum"]

model_cols = risk_factors + id_cols
df_model = df.dropna(subset=model_cols).reset_index(drop=True)

# 위험 요소 정규화
scaler = MinMaxScaler()
risk_df = pd.DataFrame(scaler.fit_transform(df_model[risk_factors]), columns=risk_factors)

# 복합 위험 점수 및 레이블
df_model["composite_risk_score"] = risk_df.sum(axis=1)
df_model["risk_label"] = pd.qcut(df_model["composite_risk_score"], q=3, labels=[0, 1, 2]).astype(int)

# 상습 결빙 구간 도로 강제 고위험 지정
high_risk_roads = freeze_df["도로(노선)명"].unique()
df_model.loc[df_model["도로명"].isin(high_risk_roads), "risk_label"] = 2

# 예측 모델링 준비
predictor_cols = equip_cols + ["경사도(%)", "avg_temp", "avg_rainfall", "avg_snowfall"] + accident_cols
df_model = df_model.dropna(subset=predictor_cols + ["risk_label"]).reset_index(drop=True)

X = df_model[predictor_cols]
y = df_model["risk_label"].astype(int)

# 스케일링 (이진 제외)
continuous_cols = ["경사도(%)", "avg_temp", "avg_rainfall", "avg_snowfall"] + accident_cols
sc = StandardScaler()
X[continuous_cols] = sc.fit_transform(X[continuous_cols])

# 학습/테스트 분리
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# 모델 학습
rf = RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_leaf=5, random_state=42)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)

# 평가
print("정확도: {:.4f}".format(accuracy_score(y_test, y_pred)))
print(classification_report(y_test, y_pred))

# 피처 중요도
importances = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
print("피처 중요도:")
print(importances)

# ========= 🌍 지도 시각화 ==============
map_center = [df_model["위도"].mean(), df_model["경도"].mean()]
m = folium.Map(location=map_center, zoom_start=14)
color_dict = {0: "green", 1: "orange", 2: "red"}

for _, row in df_model.iterrows():
    folium.CircleMarker(
        location=[row["위도"], row["경도"]],
        radius=6,
        color=color_dict.get(row["risk_label"], "blue"),
        fill=True,
        fill_color=color_dict.get(row["risk_label"], "blue"),
        fill_opacity=0.7,
        popup=f"{row['도로명']} (위험도: {row['risk_label']})"
    ).add_to(m)

m.save("광진구_위험도_지도.html")

# ========= 📊 위험도 분포 ============
plt.figure(figsize=(6,4))
sns.countplot(x="risk_label", data=df_model, palette=["green", "orange", "red"])
plt.title("위험도 분포")
plt.xlabel("위험 등급 (0=저, 1=중, 2=고)")
plt.ylabel("도로 수")
plt.tight_layout()
plt.savefig("위험도_분포_히스토그램.png")
plt.show()

# ========= 🔎 피처 중요도 ============
plt.figure(figsize=(10,6))
importances.sort_values().plot(kind="barh", color="skyblue")
plt.title("RandomForest 기반 피처 중요도")
plt.xlabel("중요도")
plt.tight_layout()
plt.savefig("피처중요도_바차트.png")
plt.show()

# ========= ❄ 상습 결빙구간만 강조된 지도 ============
freeze_roads = df_model[df_model["도로명"].isin(high_risk_roads)]
m2 = folium.Map(location=map_center, zoom_start=14)

for _, row in freeze_roads.iterrows():
    folium.CircleMarker(
        location=[row["위도"], row["경도"]],
        radius=8,
        color="darkred",
        fill=True,
        fill_color="darkred",
        fill_opacity=0.9,
        popup=f"{row['도로명']} (상습결빙)"
    ).add_to(m2)

m2.save("상습결빙구간_강조지도.html")
