import csv  # csv 파일 작업을 위한 모듈
import matplotlib.pyplot as plt  # 그래프 생성을 위한 라이브러리
def main():
    print("Hello from charmake!")
    test()
if __name__ == "__main__":
    main()
    
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

def test():
    print("test() 함수 실행 중...")
    file_path = "/Users/jichal/cpu 메인 파일/특허 로우 데이터/AA_Zoned Storage 기술의 성능 향상 191 모든 리소스.csv"
    print(f"CSV 파일 경로: {file_path}")
    csv_data = read_csv_file(file_path)
    print(f"CSV 데이터 로드 완료. 데이터 개수: {len(csv_data)}")
    if not csv_data:
        print("CSV 데이터가 비어있습니다. 차트를 생성할 수 없습니다.")
        return

    # 연도별 출원 수 계산
    year_counts = {}
    for row in csv_data:
        publication_date = row.get("Application Publication Date", "")
        if publication_date:
            year = publication_date[:4]  # 연도 추출 (YYYY-MM-DD 형식에서 앞 4자리)
            year_counts[year] = year_counts.get(year, 0) + 1
    print(f"연도별 출원 수: {year_counts}")

    if not year_counts:
        print("연도별 출원 데이터가 비어있습니다. 차트를 생성할 수 없습니다.")
        return

    # 그래프 생성
    years = sorted(year_counts.keys())
    counts = [year_counts[year] for year in years]

    plt.figure(figsize=(10, 5))  # 그래프 크기 설정
    plt.bar(years, counts, color='skyblue')  # 막대 그래프 생성
    plt.xlabel("Year")  # x축 레이블
    plt.ylabel("Number of Publications")  # y축 레이블
    plt.title("Technology Trend by Publication Year")  # 그래프 제목
    plt.savefig('chart.png')  # 그래프 저장
    print("chart.png 파일 저장 완료.")
