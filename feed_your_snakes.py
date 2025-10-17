# -*- coding: utf-8 -*-
"""
Snake Feeding Log (CSV + CLI + Charts)
======================================
功能（命令行）：
  1) 新增记录：add
  2) 查看记录：list
  3) 生成图表：charts
  4) 导出Excel：export-xlsx

示例：
  python feed.py add --name 小白 --species 玉米蛇 --food 小鼠 --weight 12.5 --appetite 强 --notes "状态很好"
  python feed.py list --name 小白 --from 2025-10-01 --to 2025-10-17
  python feed.py charts
  python feed.py export-xlsx

依赖：
  pip install pandas matplotlib xlsxwriter
"""

import os
from datetime import datetime
from typing import Optional, Dict

import argparse
import pandas as pd
import matplotlib.pyplot as plt


# -----------------------
# 全局常量与路径
# -----------------------
APPETITE_SET = ["强", "正常", "偏弱", "拒食"]

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHART_DIR = os.path.join(BASE_DIR, "charts")
CSV_PATH = os.path.join(DATA_DIR, "snake_feedings.csv")
XLSX_PATH = os.path.join(BASE_DIR, "snake_feedings.xlsx")

COLUMNS = [
    "timestamp",       # YYYY-MM-DD HH:MM:SS（本地时间）
    "snake_name",      # 蛇的姓名
    "snake_species",   # 品种/学名或常见名
    "food_species",    # 食物物种（如：小鼠、乳鼠、鹌鹑）
    "food_weight_g",   # 食物重量（克）
    "appetite",        # 进食意愿（强/正常/偏弱/拒食）
    "notes"            # 备注
]


# -----------------------
# 基础工具
# -----------------------
def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CHART_DIR, exist_ok=True)


def init_storage() -> pd.DataFrame:
    """确保 CSV 存在；若不存在则创建表头。返回当前 DataFrame。"""
    ensure_dirs()
    if not os.path.exists(CSV_PATH):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_PATH, index=False, encoding="utf-8")
        return df
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception:
        df = pd.DataFrame(columns=COLUMNS)
    return df


def save_csv(df: pd.DataFrame):
    df.to_csv(CSV_PATH, index=False, encoding="utf-8")


def load_df(parse_time: bool = True) -> pd.DataFrame:
    """加载 CSV；可解析时间列为 datetime。"""
    df = init_storage()
    if df.empty:
        return df
    if parse_time and "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    if "food_weight_g" in df.columns:
        df["food_weight_g"] = pd.to_numeric(df["food_weight_g"], errors="coerce")
    return df


# -----------------------
# 业务：新增 / 查询 / 统计 / 图表 / 导出
# -----------------------
def add_entry(
    snake_name: str,
    snake_species: str,
    food_species: str,
    food_weight_g: float,
    appetite: str,
    notes: str = "",
):
    """添加一条喂食记录到 CSV。"""
    if not snake_name.strip():
        raise ValueError("蛇的姓名不能为空")
    if not food_species.strip():
        raise ValueError("食物物种不能为空")
    try:
        weight = float(food_weight_g)
    except Exception:
        raise ValueError("食物重量必须是数字")
    if weight < 0:
        raise ValueError("食物重量必须 ≥ 0")
    if appetite not in APPETITE_SET:
        raise ValueError(f"进食意愿必须是 {APPETITE_SET} 之一")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = {
        "timestamp": timestamp,
        "snake_name": snake_name.strip(),
        "snake_species": snake_species.strip(),
        "food_species": food_species.strip(),
        "food_weight_g": weight,
        "appetite": appetite,
        "notes": notes.strip(),
    }

    df = init_storage()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    save_csv(df)
    print(f"✅ 已保存：{CSV_PATH}")


def list_entries(
    name: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 50,
):
    """列出记录（可按蛇名与时间范围过滤）。"""
    df = load_df(parse_time=True)
    if df.empty:
        print("（暂无记录）")
        return

    q = df
    if name:
        q = q[q["snake_name"] == name]
    if date_from:
        try:
            dt_from = pd.to_datetime(date_from)
            q = q[q["timestamp"] >= dt_from]
        except Exception:
            print("警告：--from 无法解析，已忽略。")
    if date_to:
        try:
            dt_to = pd.to_datetime(date_to)
            q = q[q["timestamp"] <= dt_to]
        except Exception:
            print("警告：--to 无法解析，已忽略。")

    q = q.sort_values("timestamp", ascending=False)
    if limit and limit > 0:
        q = q.head(limit)
    if q.empty:
        print("（筛选后无记录）")
        return

    # 更友好显示
    out = q.copy()
    out["timestamp"] = out["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    print(out.to_string(index=False))
    print(f"\n共 {len(q)} 条（已按时间倒序显示，文件：{CSV_PATH}）")


def weekly_sum(df: pd.DataFrame) -> pd.DataFrame:
    """计算每蛇每周总摄入克数（周起始为周一/周日均可，这里用周日）。"""
    if df.empty:
        return df
    temp = df.dropna(subset=["timestamp"]).copy()
    temp["week"] = temp["timestamp"].dt.to_period("W-SUN").apply(lambda r: r.start_time.date())
    gp = temp.groupby(["snake_name", "week"], as_index=False)["food_weight_g"].sum()
    return gp


def compute_intervals_days(df: pd.DataFrame) -> pd.DataFrame:
    """按蛇分组、按时间排序，计算与上一次喂食的间隔（天）。"""
    if df.empty:
        return df
    df = df.copy()
    df = df.sort_values(["snake_name", "timestamp"])
    df["prev_time"] = df.groupby("snake_name")["timestamp"].shift(1)
    df["interval_days"] = (df["timestamp"] - df["prev_time"]).dt.total_seconds() / 86400.0
    return df


def make_charts():
    """生成 4 张图：总摄入（按蛇）、周趋势、意愿分布、间隔分布。"""
    df = load_df(parse_time=True)
    if df.empty:
        print("暂无数据，无法生成图表。")
        return
    ensure_dirs()

    # 图1：按蛇累计摄入克数（柱状图）
    total_by_snake = df.groupby("snake_name", as_index=False)["food_weight_g"].sum()
    total_by_snake = total_by_snake.sort_values("food_weight_g", ascending=False)
    plt.figure()
    plt.bar(total_by_snake["snake_name"], total_by_snake["food_weight_g"])
    plt.title("按蛇累计摄入克数")
    plt.xlabel("蛇")
    plt.ylabel("总克数")
    plt.xticks(rotation=30, ha="right")
    path1 = os.path.join(CHART_DIR, "total_by_snake.png")
    plt.tight_layout(); plt.savefig(path1, dpi=150); plt.close()

    # 图2：每蛇的周摄入趋势（折线图）
    wk = weekly_sum(df)
    if not wk.empty:
        plt.figure()
        for name in wk["snake_name"].unique():
            sub = wk[wk["snake_name"] == name]
            plt.plot(sub["week"], sub["food_weight_g"], marker="o", label=name)
        plt.title("每蛇周摄入趋势")
        plt.xlabel("周起始日")
        plt.ylabel("总克数/周")
        plt.xticks(rotation=30, ha="right")
        plt.legend()
        path2 = os.path.join(CHART_DIR, "weekly_trend.png")
        plt.tight_layout(); plt.savefig(path2, dpi=150); plt.close()

    # 图3：进食意愿分布（条形图）
    appetite_count = df["appetite"].value_counts().reindex(APPETITE_SET, fill_value=0)
    plt.figure()
    plt.bar(appetite_count.index, appetite_count.values)
    plt.title("进食意愿分布")
    plt.xlabel("意愿")
    plt.ylabel("次数")
    path3 = os.path.join(CHART_DIR, "appetite_distribution.png")
    plt.tight_layout(); plt.savefig(path3, dpi=150); plt.close()

    # 图4：与上次喂食间隔（天）（箱形图）
    with_interval = compute_intervals_days(df).dropna(subset=["interval_days"])
    if not with_interval.empty:
        plt.figure()
        groups = [g["interval_days"].values for _, g in with_interval.groupby("snake_name")]
        labels = [name for name, _ in with_interval.groupby("snake_name")]
        plt.boxplot(groups, labels=labels, showmeans=True)
        plt.title("与上次喂食间隔（天）- 箱形图")
        plt.xlabel("蛇")
        plt.ylabel("天数")
        plt.xticks(rotation=30, ha="right")
        path4 = os.path.join(CHART_DIR, "interval_boxplot.png")
        plt.tight_layout(); plt.savefig(path4, dpi=150); plt.close()

    print("✅ 图表已输出到 ./charts/ ：")
    for p in [locals().get(f"path{i}") for i in range(1, 5)]:
        if p and os.path.exists(p):
            print(" -", p)


def build_summary_tables(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """构建用于 Excel 的统计表。"""
    res = {}

    if df.empty:
        res["summary_by_snake"] = pd.DataFrame(columns=["snake_name", "total_g", "count", "mean_g", "last_feed", "last_30d_count", "refusal_rate"])
        res["summary_by_food"] = pd.DataFrame(columns=["food_species", "total_g", "count"])
        return res

    # 每蛇统计
    last_feed = df.sort_values("timestamp").groupby("snake_name", as_index=False)["timestamp"].last()
    by_snake = df.groupby("snake_name", as_index=False).agg(
        total_g=("food_weight_g", "sum"),
        count=("food_weight_g", "count"),
        mean_g=("food_weight_g", "mean"),
    )
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=30)
    recent = df[df["timestamp"] >= cutoff]
    last30 = recent.groupby("snake_name", as_index=False)["food_weight_g"].count().rename(columns={"food_weight_g": "last_30d_count"})
    refusal = df.assign(is_refusal=df["appetite"].eq("拒食").astype(int)).groupby("snake_name", as_index=False)["is_refusal"].mean().rename(columns={"is_refusal": "refusal_rate"})

    summary_snake = by_snake.merge(last_feed, on="snake_name", how="left") \
                            .merge(last30, on="snake_name", how="left") \
                            .merge(refusal, on="snake_name", how="left")
    summary_snake["last_30d_count"] = summary_snake["last_30d_count"].fillna(0).astype(int)
    summary_snake["refusal_rate"] = summary_snake["refusal_rate"].fillna(0.0).round(3)

    res["summary_by_snake"] = summary_snake.sort_values("total_g", ascending=False)

    # 每食物物种统计
    summary_food = df.groupby("food_species", as_index=False).agg(
        total_g=("food_weight_g", "sum"),
        count=("food_weight_g", "count")
    ).sort_values("total_g", ascending=False)
    res["summary_by_food"] = summary_food

    return res


def export_excel():
    """导出 Excel：feedings 明细 + 两张统计表。"""
    df = load_df(parse_time=True)
    if df.empty:
        print("暂无数据，取消导出。")
        return

    tables = build_summary_tables(df)
    try:
        with pd.ExcelWriter(XLSX_PATH, engine="xlsxwriter") as writer:
            out_df = df.sort_values("timestamp", ascending=False).copy()
            out_df["timestamp"] = out_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
            out_df.to_excel(writer, index=False, sheet_name="feedings")

            tables["summary_by_snake"].to_excel(writer, index=False, sheet_name="summary_by_snake")
            tables["summary_by_food"].to_excel(writer, index=False, sheet_name="summary_by_food")

            for sheet in ["feedings", "summary_by_snake", "summary_by_food"]:
                ws = writer.sheets[sheet]
                ws.set_column(0, 0, 20)
                ws.set_column(1, 3, 16)
                ws.set_column(4, 6, 12)

        print(f"✅ 已导出：{XLSX_PATH}")
    except Exception as e:
        print("导出失败：", e)


# -----------------------
# argparse 命令定义
# -----------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="蛇类喂食记录（CSV + CLI + 图表）",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # add
    ap = sub.add_parser("add", help="新增一条喂食记录")
    ap.add_argument("--name", required=True, help="蛇的姓名")
    ap.add_argument("--species", default="", help="蛇的品种/学名（可空）")
    ap.add_argument("--food", required=True, help="食物物种（如：小鼠/乳鼠/鹌鹑）")
    ap.add_argument("--weight", required=True, type=float, help="食物重量（克，≥0）")
    ap.add_argument("--appetite", required=True, choices=APPETITE_SET, help="进食意愿")
    ap.add_argument("--notes", default="", help="备注（可空）")

    # list
    lp = sub.add_parser("list", help="查看记录（支持筛选）")
    lp.add_argument("--name", help="按蛇名筛选", default=None)
    lp.add_argument("--from", dest="date_from", help="起始日期 YYYY-MM-DD", default=None)
    lp.add_argument("--to", dest="date_to", help="结束日期 YYYY-MM-DD", default=None)
    lp.add_argument("--limit", type=int, default=50, help="显示条数（倒序）")

    # charts
    cp = sub.add_parser("charts", help="生成图表到 ./charts/")

    # export-xlsx
    ep = sub.add_parser("export-xlsx", help="导出 Excel（含明细与统计）")

    return p


def main():
    init_storage()
    parser = build_parser()
    args = parser.parse_args()

    if args.cmd == "add":
        add_entry(
            snake_name=args.name,
            snake_species=args.species or "",
            food_species=args.food,
            food_weight_g=args.weight,
            appetite=args.appetite,
            notes=args.notes or "",
        )
    elif args.cmd == "list":
        list_entries(
            name=args.name,
            date_from=args.date_from,
            date_to=args.date_to,
            limit=args.limit,
        )
    elif args.cmd == "charts":
        make_charts()
    elif args.cmd == "export-xlsx":
        export_excel()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
