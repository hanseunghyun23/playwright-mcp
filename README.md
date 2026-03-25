# 두산 베어스 타율 데이터 수집 및 시각화

> **KBO 실데이터를 자동 수집하고, 팀 평균과 주요 선수 3인의 타율 추이를 비교 분석하는 파이프라인**



---

## 프로젝트 개요

KBO 리그 두산 베어스의 팀 타율 데이터(2015~2025)를 **Playwright MCP**를 활용해 웹에서 자동 수집하고, 핵심 선수(박건우·양의지·오재일)의 개인 타율과 함께 시각화한 데이터 분석 프로젝트입니다.

단순한 차트 생성을 넘어, **데이터 수집 → 정제 → 병합 → 시각화**까지 이어지는 전체 파이프라인을 구현했습니다.

---

## 기술 스택

| 분류 | 기술 |
|------|------|
| Language | Python 3 |
| Data Collection | Playwright MCP (AI-driven 웹 자동화) |
| Data Processing | pandas |
| Visualization | matplotlib |
| IDE | Cursor AI |

---

## 프로젝트 구조

```
playwright-mcp-main/
├── plot_batting_averages.py              # 메인 스크립트 (데이터 처리 + 시각화)
├── player_batting_averages_2015_2022.csv # 선수별 타율 데이터
├── doosan_bears_batting_average_2015_2025.html  # 팀 평균 타율 데이터 (수집 결과)
├── batting_average_plot.png              # 최종 시각화 결과물
└── .cursor/
    └── mcp.json                          # Playwright MCP 서버 설정
```

---

## 주요 기능

### 1. Playwright MCP를 활용한 데이터 자동 수집
Cursor AI 환경에서 **Playwright MCP 서버**를 연동해 KBO 공식 데이터를 자동으로 수집합니다. AI가 직접 브라우저를 조작해 데이터를 추출하며, 결과는 HTML 형식으로 저장됩니다.

```json
// .cursor/mcp.json
{
  "mcpServers": {
    "playwright": {
      "command": "bunx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

### 2. 이기종 데이터 파싱 및 병합
CSV(선수 데이터)와 HTML 테이블(팀 데이터)을 각각 파싱한 뒤 연도 기준으로 병합합니다.

```python
def read_players_csv(csv_path):
    # CSV에서 선수별 타율 로드 및 타입 정제
    ...

def read_doosan_html(html_path):
    # HTML 테이블 파싱, 2015~2025 구간 필터링
    ...

def merge_for_plot(players_df, doosan_df):
    # 연도 기준 outer merge
    ...
```

### 3. 선수 재적 기간 반영 시각화
각 선수의 두산 실제 재적 기간에 맞춰 그래프 표시 구간을 제어합니다.

| 선수 | 표시 구간 |
|------|-----------|
| 박건우 | 2016 ~ 2021 |
| 양의지 | 2015~2018, 2023~ |
| 오재일 | 2016 ~ 2020 |

---

## 분석 결과

두산 베어스 팀 타율(2015~2025) 추이와 핵심 선수들의 개인 타율을 비교했을 때 주요 발견점은 다음과 같습니다.

- **2018년** 두산 팀 타율 최고점(0.309) — 양의지(0.358), 박건우(0.326) 모두 커리어 하이 시즌과 겹침
- **2020년 이후** 팀 타율 하락세(0.293 → 0.255)는 핵심 타자 이탈 시점과 일치
- **양의지 복귀 이후(2023~)** 개인 타율은 회복세이나 팀 전체 수치는 여전히 낮은 수준 유지

---

## 실행 방법

### 사전 준비
```bash
pip install matplotlib pandas
```

### 그래프 생성
```bash
python plot_batting_averages.py
# → batting_average_plot.png 생성
```

### Playwright MCP 설정 (데이터 재수집 시)
```bash
# bun 설치 후
bunx @playwright/mcp@latest
```

---

## 배운 점 / 의의

- **Playwright MCP**를 Cursor AI와 연동해 AI가 직접 웹 데이터를 수집하는 자동화 파이프라인을 구현
- 실제 스포츠 데이터를 활용해 이기종 포맷(CSV, HTML) 데이터 정제·병합 경험
- 선수 이적 이력 등 도메인 지식을 코드에 반영하는 데이터 모델링 설계
