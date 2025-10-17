import pandas as pd

path = r"F:\e盘\programme\python\data\snake_feedings.csv"

# 创建空表头
columns = [
    "timestamp", "snake_name", "snake_species",
    "food_species", "food_weight_g", "appetite", "notes"
]
pd.DataFrame(columns=columns).to_csv(path, index=False, encoding="utf-8")

print("✅ 已清空所有喂食记录，但保留了表头。")
