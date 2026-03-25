from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd


def read_players_csv(csv_path: Path) -> pd.DataFrame:

    df = pd.read_csv(csv_path)
    df.rename(columns={df.columns[0]: "연도"}, inplace=True)
    df["연도"] = pd.to_numeric(df["연도"], errors="coerce").astype("Int64")

    for player in ["박건우", "양의지", "오재일"]:
        if player in df.columns:
            df[player] = pd.to_numeric(df[player], errors="coerce")

    df = df.dropna(subset=["연도"]).astype({"연도": "int"})
    return df


def read_doosan_html(html_path: Path) -> pd.DataFrame:

    tables = pd.read_html(html_path)
    if len(tables) == 0:
        raise ValueError("HTML에서 테이블을 찾을 수 없습니다.")

    table = tables[0]
    # 기대 컬럼: 연도, 타율, 비고
    # 평균 행(예: '11년 평균') 제거 및 숫자 연도만 남기기
    table = table.copy()
    table.rename(columns={table.columns[0]: "연도", table.columns[1]: "타율"}, inplace=True)
    table["연도"] = pd.to_numeric(table["연도"], errors="coerce")
    table["타율"] = pd.to_numeric(table["타율"], errors="coerce")
    table = table.dropna(subset=["연도", "타율"]).astype({"연도": "int"})

    # 관심 구간만 남기기 (2015~2025)
    table = table[(table["연도"] >= 2015) & (table["연도"] <= 2025)][["연도", "타율"]]
    table = table.sort_values("연도").reset_index(drop=True)
    return table


def merge_for_plot(players_df: pd.DataFrame, doosan_df: pd.DataFrame) -> pd.DataFrame:

    merged = pd.merge(doosan_df, players_df, on="연도", how="outer")
    merged = merged.sort_values("연도").reset_index(drop=True)
    return merged


def plot_batting_averages(merged_df: pd.DataFrame, output_path: Path) -> None:

    plt.rcParams["font.family"] = ["Malgun Gothic", "Apple SD Gothic Neo", "NanumGothic", "Arial"]

    fig, ax = plt.subplots(figsize=(12, 6))

    # 양의지 누락 연도 수집값으로 보강 (필요시 업데이트)
    if "양의지" in merged_df.columns:
        yang_fill = {
            2015: 0.326,
            2016: 0.325,
            2017: 0.339,
            2023: 0.305,
            2024: 0.314,
            2025: 0.337,
        }
        for year, avg in yang_fill.items():
            mask = merged_df["연도"] == year
            if mask.any():
                if pd.isna(merged_df.loc[mask, "양의지"]).all():
                    merged_df.loc[mask, "양의지"] = avg

    # 오재일 2015년 누락값 보강
    if "오재일" in merged_df.columns:
        mask_oh_2015 = merged_df["연도"] == 2015
        if mask_oh_2015.any():
            if pd.isna(merged_df.loc[mask_oh_2015, "오재일"]).all():
                merged_df.loc[mask_oh_2015, "오재일"] = 0.289

    # 두산 팀 평균 (HTML)
    if "타율" in merged_df.columns:
        ax.plot(
            merged_df["연도"],
            merged_df["타율"],
            label="두산 평균",
            color="#1f77b4",
            linewidth=2.5,
            marker="o",
        )

    # 세 선수 (CSV) - 요청 범위만 반영하여 그리기
    years = merged_df["연도"]
    player_colors: Dict[str, str] = {"박건우": "#2ca02c", "양의지": "#ff7f0e", "오재일": "#9467bd"}

    # 각 선수별 연도 조건 정의
    player_year_conditions: Dict[str, pd.Series] = {}
    if "양의지" in merged_df.columns:
        cond_yang = ((years >= 2015) & (years <= 2018)) | (years >= 2023)
        player_year_conditions["양의지"] = cond_yang
    if "오재일" in merged_df.columns:
        cond_oh = years <= 2020
        player_year_conditions["오재일"] = cond_oh
    if "박건우" in merged_df.columns:
        cond_park = years <= 2021
        player_year_conditions["박건우"] = cond_park

    for player, color in player_colors.items():
        if player in merged_df.columns:
            series = merged_df[player]
            cond = player_year_conditions.get(player, pd.Series([False] * len(series)))
            filtered = series.where(cond)
            ax.plot(
                years,
                filtered,
                label=player,
                linewidth=2,
                marker="o",
                color=color,
            )

    ax.set_title("두산 평균 vs. 선수별 타율 추이 (2015-2025)")
    ax.set_xlabel("연도")
    ax.set_ylabel("타율")
    # 모든 시리즈(두산+세 선수)를 고려해 y축을 자동 범위로 설정
    y_columns = [col for col in ["타율", "박건우", "양의지", "오재일"] if col in merged_df.columns]
    y_values = pd.concat([merged_df[col] for col in y_columns], axis=0).dropna()
    if not y_values.empty:
        y_min = float(y_values.min())
        y_max = float(y_values.max())
        padding = max(0.005, (y_max - y_min) * 0.1)
        ax.set_ylim(max(0.0, y_min - padding), min(1.0, y_max + padding))
    ax.grid(True, alpha=0.2)
    ax.legend(loc="best")

    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def main() -> None:

    base = Path(__file__).parent
    csv_path = base / "player_batting_averages_2015_2022.csv"
    html_path = base / "doosan_bears_batting_average_2015_2025.html"
    output_path = base / "batting_average_plot.png"

    players_df = read_players_csv(csv_path)
    doosan_df = read_doosan_html(html_path)
    merged_df = merge_for_plot(players_df, doosan_df)

    plot_batting_averages(merged_df, output_path)
    print(f"그래프 저장 완료: {output_path}")


if __name__ == "__main__":
    main()


