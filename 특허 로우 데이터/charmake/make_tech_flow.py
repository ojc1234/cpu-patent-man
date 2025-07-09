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

def main():
    file_path = "/Users/jichal/cpu 메인 파일/특허 로우 데이터/AA_Zoned Storage 기술의 성능 향상 191 모든 리소스.csv"
    csv_data = read_csv_file(file_path)

    if not csv_data:
        print("CSV 데이터가 비어있습니다.")
        return

    # Assignee별 특허를 연도순으로 정렬
    assignee_patents = defaultdict(lambda: defaultdict(list))
    for row in csv_data:
        assignee = row.get("Assignee", "Unknown")
        pub_date = row.get("Application Publication Date", "")
        title = row.get("Title", "No Title")

        if pub_date and len(pub_date) >= 4:
            year = pub_date[:4]
            assignee_patents[assignee][year].append(title)

    # 발명자 수별 연도별 특허 출원 수 집계
    # {num_inventors: {year: count_of_patents}}
    inventor_yearly_patent_counts = defaultdict(lambda: defaultdict(int))
    all_years = set()
    all_num_inventors = set()

    for row in csv_data:
        inventors_str = row.get("Inventors", "")
        pub_date = row.get("Application Publication Date", "")

        if inventors_str and pub_date and len(pub_date) >= 4:
            inventor_list = [inv.strip() for inv in inventors_str.split('|') if inv.strip()]
            num_inventors = len(inventor_list)
            year = pub_date[:4]

            if num_inventors > 0:
                inventor_yearly_patent_counts[num_inventors][year] += 1
                all_years.add(year)
                all_num_inventors.add(num_inventors)

    sorted_years = sorted(list(all_years))
    sorted_num_inventors = sorted(list(all_num_inventors))

    # 기술성장도 맵을 위한 데이터 준비
    # 연도별 고유 발명자 수 및 총 출원 건수 집계 (이전 단계와 동일)
    unique_inventors_per_year = defaultdict(set)
    total_applications_per_year = defaultdict(int)
    all_years = set()

    for row in csv_data:
        pub_date = row.get("Application Publication Date", "")
        inventors_str = row.get("Inventors", "")

        if pub_date and len(pub_date) >= 4:
            year = pub_date[:4]
            # 2024년과 2025년 데이터 제외
            if year in ['2024', '2025']:
                continue 

            all_years.add(year)
            total_applications_per_year[year] += 1

            if inventors_str:
                inventor_names = [inv.strip() for inv in inventors_str.split('|') if inv.strip()]
                for inventor in inventor_names:
                    unique_inventors_per_year[year].add(inventor)

    sorted_years = sorted(list(all_years))
    
    # X축: 고유 발명자 수, Y축: 총 출원 건수 (반전)
    x_inventors = [len(unique_inventors_per_year[year]) for year in sorted_years]
    y_applications = [total_applications_per_year[year] for year in sorted_years]

    # 그래프 생성: 기술성장도 맵 (강화된 버전)
    plt.figure(figsize=(12, 10))

    # 연도별 흐름을 보여주기 위해 선과 화살표로 연결
    plt.plot(x_inventors, y_applications, linestyle='-', color='darkblue', alpha=0.8, linewidth=1.5, zorder=1)

    # 각 점(연도)에 버블 형태로 표시하고 연도 라벨 추가
    for i, year in enumerate(sorted_years):
        # 버블 크기 (조정 가능) - 연도가 많아질수록 커지도록
        current_year_int = int(year)
        min_year_int = int(sorted_years[0]) # 가장 오래된 연도
        bubble_size = 100 + (current_year_int - min_year_int) * 300 # 연도 차이에 비례하여 크기 대폭 증가

        # 무지개 색상 맵에서 현재 연도에 해당하는 색상 가져오기
        cmap_rainbow = plt.cm.get_cmap('rainbow_r', len(sorted_years)) # 색상 맵 반전
        bubble_color = cmap_rainbow(i) # 'i'는 sorted_years에서의 인덱스

        plt.scatter(x_inventors[i], y_applications[i], s=bubble_size, color=bubble_color, edgecolor='black', linewidth=1.5, alpha=0.5, zorder=2) # 투명도 0.5로 설정
        
        # 연도 라벨을 점 옆에 표시
        plt.annotate(year, (x_inventors[i], y_applications[i]),
                     textcoords="offset points", xytext=(8,8), ha='center', fontsize=9, color='black',
                     bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="darkgrey", lw=0.5, alpha=0.7), zorder=3)

    # 화살표 추가
    for i in range(len(sorted_years) - 1):
        x_start, y_start = x_inventors[i], y_applications[i]
        x_end, y_end = x_inventors[i+1], y_applications[i+1]
        
        # 화살표가 너무 짧으면 생략하거나, 시작점/끝점 조정
        plt.annotate("",
                     xy=(x_end, y_end), xycoords='data',
                     xytext=(x_start, y_start), textcoords='data',
                     arrowprops=dict(arrowstyle="->", color='gray', lw=1.5, linestyle='-', shrinkA=5, shrinkB=5, patchA=None, patchB=None, connectionstyle="arc3,rad=0.0"),
                     zorder=1) # 선 뒤에 오도록 zorder 설정

    plt.xlabel("고유 발명자 수")
    plt.ylabel("총 출원 건수")
    plt.title("기술성장도 맵 (Technology Maturity Map)")
    plt.grid(True, linestyle='--', alpha=0.6)

    # X, Y 축 레이블 자동 조정 방지 (필요시)
    # plt.autoscale(enable=True, axis='both', tight=True)
    # plt.xlim(min(x_applications)*0.8, max(x_applications)*1.2)
    # plt.ylim(min(y_inventors)*0.8, max(y_inventors)*1.2)

    plt.tight_layout()
    plt.savefig('technology_maturity_map.png')
    print("technology_maturity_map.png 파일이 생성되었습니다.")

if __name__ == "__main__":
    main()
