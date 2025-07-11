import csv
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib.font_manager as fm # 폰트 관리자 임포트

# 한글 폰트 설정 (macOS의 경우 AppleGothic, Windows의 경우 Malgun Gothic 등)
# 시스템에 폰트가 없을 경우 오류가 발생할 수 있습니다.
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False # 마이너스 부호 깨짐 방지

def read_csv_file(file_path):
    """
    Reads a CSV file and returns the data as a list of dictionaries.
    Each dictionary represents a row in the CSV file, with keys being the column headers.
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

def get_interval_start_year(year, interval_size):
    """
    Calculates the start year of the interval for a given year based on the interval_size.
    E.g., for interval_size=3, 2010-2012 -> 2010, 2013-2015 -> 2013.
    """
    return (year // interval_size) * interval_size

def main():
    file_path = "/Users/jichal/cpu 메인 파일/특허 로우 데이터/AB_ Zoned Storage 유지관리 기술의 성능 향상 826 모든 리소스.csv"
    csv_data = read_csv_file(file_path)

    if not csv_data:
        print("CSV 데이터가 비어있습니다.")
        return

    # 기술성장도 맵을 위한 데이터 준비
    # 3년 단위로 고유 출원인 수 및 총 출원 건수 집계
    unique_assignees_per_interval = defaultdict(set)
    total_applications_per_interval = defaultdict(int)
    all_intervals = set()
    interval_size = 3

    for row in csv_data:
        pub_date = row.get("Application Publication Date", "")
        assignee_str = row.get("Assignee", "")

        if pub_date and len(pub_date) >= 4:
            year = int(pub_date[:4])
            # Filter data to include only years between 2010 and 2023
            if not (2010 <= year <= 2023):
                continue 

            interval = get_interval_start_year(year, interval_size)
            all_intervals.add(interval)
            total_applications_per_interval[interval] += 1

            if assignee_str:
                assignee_names = [assign.strip() for assign in assignee_str.split('|') if assign.strip()]
                for assignee in assignee_names:
                    unique_assignees_per_interval[interval].add(assignee)

    sorted_intervals = sorted(list(all_intervals))
    
    # X축: 고유 출원인 수, Y축: 총 출원 건수 (반전)
    x_assignees = [len(unique_assignees_per_interval[interval]) for interval in sorted_intervals]
    y_applications = [total_applications_per_interval[interval] for interval in sorted_intervals]

    # 그래프 생성: 기술성장도 맵 (강화된 버전)
    plt.figure(figsize=(12, 10))

    # 연도별 흐름을 보여주기 위해 선과 화살표로 연결
    plt.plot(x_assignees, y_applications, linestyle='-', color='darkblue', alpha=0.8, linewidth=1.5, zorder=1)

    # 각 점(연도)에 버블 형태로 표시하고 연도 라벨 추가
    for i, interval in enumerate(sorted_intervals):
        # 버블 크기 (조정 가능) - 연도가 많아질수록 커지도록
        min_interval_int = sorted_intervals[0] # 가장 오래된 연도
        bubble_size = 100 + (interval - min_interval_int) * 300 # 연도 차이에 비례하여 크기 대폭 증가

        # 무지개 색상 맵에서 현재 연도에 해당하는 색상 가져오기
        cmap_rainbow = plt.cm.get_cmap('rainbow_r', len(sorted_intervals)) # 색상 맵 반전
        bubble_color = cmap_rainbow(i) # 'i'는 sorted_intervals에서의 인덱스

        plt.scatter(x_assignees[i], y_applications[i], s=bubble_size, color=bubble_color, edgecolor='black', linewidth=1.5, alpha=0.5, zorder=2) # 투명도 0.5로 설정
        
        # Determine the end year for the label, ensuring it doesn't exceed 2023
        label_end_year = interval + interval_size - 1
        if interval == sorted_intervals[-1] and label_end_year > 2023:
            label_end_year = 2023 # Ensure the last label doesn't go beyond 2023

        # 연도 라벨을 점 옆에 표시 (3년 간격으로 표시)
        plt.annotate(f"{interval}-{label_end_year}", (x_assignees[i], y_applications[i]),
                     textcoords="offset points", xytext=(8,8), ha='center', fontsize=9, color='black',
                     bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="darkgrey", lw=0.5, alpha=0.7), zorder=3)

    # 화살표 추가
    for i in range(len(sorted_intervals) - 1):
        x_start, y_start = x_assignees[i], y_applications[i]
        x_end, y_end = x_assignees[i+1], y_applications[i+1]
        
        # 화살표가 너무 짧으면 생략하거나, 시작점/끝점 조정
        plt.annotate("",
                     xy=(x_end, y_end), xycoords='data',
                     xytext=(x_start, y_start), textcoords='data',
                     arrowprops=dict(arrowstyle="->", color='gray', lw=1.5, linestyle='-', shrinkA=5, shrinkB=5, patchA=None, patchB=None, connectionstyle="arc3,rad=0.0"),
                     zorder=1) # 선 뒤에 오도록 zorder 설정

    plt.xlabel("출원인 수")
    plt.ylabel("총 출원 건수")
    plt.title("AB 기술성장도 맵 (3년 합산)")
    plt.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.savefig('AB_technology_maturity_map_3year_aggregated.png')
    print("AB_technology_maturity_map_3year_aggregated.png 파일이 생성되었습니다.")

if __name__ == "__main__":
    main()
