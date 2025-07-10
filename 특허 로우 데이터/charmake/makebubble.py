import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from adjustText import adjust_text
def set_korean_font():
    """
    macOS와 Windows 환경에 맞는 한글 폰트를 설정합니다.
    """
    # --- 1. 한글 폰트 설정 ---
    try:
        # 폰트 우선순위 설정
        # 1. Apple SD Gothic Neo 또는 AppleGothic을 우선적으로 시도합니다.
        # 2. 없으면 NanumGothic 또는 Malgun Gothic을 시도합니다.
        # 3. 모든 한글 폰트가 없으면 'Apple Color Emoji'를 포함한 시스템 기본 폰트 사용
        
        chosen_font_name = None
        font_paths_to_try = [
            'Apple SD Gothic Neo', 'AppleGothic', 'NanumGothic', 'Malgun Gothic'
        ]

        for font_name_to_try in font_paths_to_try:
            font_path = fm.findfont(font_name_to_try)
            if font_path:
                chosen_font_name = fm.FontProperties(fname=font_path).get_name()
                print(f"'{chosen_font_name}' 폰트가 성공적으로 설정될 예정입니다.")
                break
        
        if chosen_font_name:
            plt.rcParams['font.family'] = [chosen_font_name, 'Apple Color Emoji', 'sans-serif']
        else:
            plt.rcParams['font.family'] = ['Apple Color Emoji', 'sans-serif']
            print("경고: 적절한 한글 폰트를 찾을 수 없습니다. 'NanumGothic' 또는 'Apple SD Gothic Neo' 폰트 설치를 권장합니다.")
        
        # 마이너스 부호가 깨지는 문제 해결
        plt.rcParams['axes.unicode_minus'] = False
        print(f"Matplotlib에 설정된 최종 폰트 패밀리: {plt.rcParams['font.family']}")
    except Exception as e:
        print(f"폰트 설정 중 오류가 발생했습니다: {e}")
        print("기본 폰트로 차트를 생성합니다. 한글이 깨질 수 있습니다. 한글 폰트 설치를 권장합니다.")

def load_and_preprocess_data(file_path):
    """CSV 파일을 로드하고 전처리하여 분석에 적합한 DataFrame을 반환합니다."""
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except FileNotFoundError:
        print(f"오류: 파일을 찾을 수 없습니다 - {file_path}")
        return
    except Exception as e:
        print(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        return

    # 'Revenue' 열을 숫자형으로 변환
    def clean_revenue(revenue_str):
        if isinstance(revenue_str, str):
            # 'US$', ',' 제거 후 float으로 변환
            cleaned_str = revenue_str.replace('US$', '').replace(',', '')
            try:
                return float(cleaned_str)
            except ValueError:
                return 0.0
        return revenue_str

    # 필요한 열들을 숫자형으로 변환
    df['Revenue_Clean'] = df['Revenue'].apply(clean_revenue)
    df['Vision'] = pd.to_numeric(df['Vision (% Patents + % Classifications + % Citations)'], errors='coerce')
    df['Resources'] = pd.to_numeric(df['Resources (% Revenue + % Locations + % Litigation)'], errors='coerce')
    df['Patents'] = pd.to_numeric(df['Patents'], errors='coerce')

    # 필수 데이터가 없는 행 제거
    df.dropna(subset=['Vision', 'Resources', 'Patents', 'Organization'], inplace=True)

    return df

def create_bubble_chart(df):
    """
    전처리된 DataFrame을 사용하여 기업별 특허 포트폴리오 버블 차트를 생성합니다.
    """
    if df.empty:
        print("차트를 그릴 데이터가 없습니다. CSV 파일의 내용을 확인해주세요.")
        return

    # --- 1. 차트 기본 설정 ---
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(18, 12))

    # --- 2. 버블 차트 생성 ---
    colors = plt.cm.viridis(np.linspace(0, 1, len(df)))
    # 버블 크기를 'Patents' 수에 따라 조절 (가시성을 위해 200을 곱함)
    bubble_size = df['Patents'] * 200

    scatter = plt.scatter(
        x=df['Vision'],
        y=df['Resources'],
        s=bubble_size,
        c=colors,
        alpha=0.7,
        edgecolors="w",
        linewidth=2
    )

    # --- 3. 텍스트 레이블 최적화 ---
    # adjust_text를 사용하여 텍스트가 겹치지 않도록 조정
    texts = []
    for i, row in df.iterrows():
        texts.append(plt.text(row['Vision'], row['Resources'], row['Organization'],
                              fontsize=10, ha='center', va='center', weight='bold'))
    
    adjust_text(texts, arrowprops=dict(arrowstyle='->', color='red', lw=0.5))

    # --- 4. 차트 제목 및 레이블 설정 ---
    plt.title('기업별 특허 포트폴리오 분석 (Bubble Chart)', fontsize=22, pad=20)
    plt.xlabel('Vision (% Patents + % Classifications + % Citations)', fontsize=16)
    plt.ylabel('Resources (% Revenue + % Locations + % Litigation)', fontsize=16)
    
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.savefig('./chartbubble.png')  # 그래프 저장
def main():
    # 1. 한글 폰트 설정
        set_korean_font()
        # 2. 데이터 로드 및 전처리
        csv_file_path = '/Users/jichal/cpu 메인 파일/특허 로우 데이터/Data-표 1.csv'
        processed_df = load_and_preprocess_data(csv_file_path)
        # 3. 버블 차트 생성
        if processed_df is not None:
            create_bubble_chart(processed_df)

if __name__ == '__main__':
    main()
