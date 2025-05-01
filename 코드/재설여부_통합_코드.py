import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from scipy.spatial import cKDTree

# [1] 도로 데이터 불러오기 (열선 여부까지 붙인 파일)
road_df = pd.read_csv("광진구_도로명_위경도_경사도_열선설치.csv")
road_gdf = gpd.GeoDataFrame(
    road_df,
    geometry=gpd.points_from_xy(road_df['경도'], road_df['위도']),
    crs="EPSG:4326"
).to_crs(epsg=5186)

# [2] 제설함 데이터 불러오기
snow_df = pd.read_csv("데이터셋/광진구_제설함_위치정보.csv",  encoding='cp949')
snow_gdf = gpd.GeoDataFrame(
    snow_df,
    geometry=gpd.points_from_xy(snow_df['경도'], snow_df['위도']),
    crs="EPSG:4326"
).to_crs(epsg=5186)

# [3] KDTree 생성
snow_coords = np.array(list(zip(snow_gdf.geometry.x, snow_gdf.geometry.y)))
tree_snow = cKDTree(snow_coords)

# [4] 도로 포인트 준비
road_coords = np.array(list(zip(road_gdf.geometry.x, road_gdf.geometry.y)))

# [5] 거리 매칭 (50m 이내)
dist_snow, idx_snow = tree_snow.query(road_coords, distance_upper_bound=50)

# [6] 50m 이내에 매칭되면 '제설함 있음' 1, 없으면 0
road_gdf['제설함여부'] = np.where(dist_snow != np.inf, 1, 0)

# [7] 결과 저장
final_cols = ['도로명', '전체주소', '위도', '경도', '경사도(%)', '열선설치여부', '제설함여부']
road_gdf[final_cols].to_csv("광진구_제설함통합.csv", index=False)

print("✅ 제설함 거리 계산 완료 및 병합! 결과 저장: 열선도로, 제설함 통합.csv")
