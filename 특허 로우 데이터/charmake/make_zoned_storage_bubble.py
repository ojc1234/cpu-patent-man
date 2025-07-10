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
        return pd.DataFrame() # Return empty DataFrame on error
    except Exception as e:
        print(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame() # Return empty DataFrame on error

    # Extract year from 'Application Publication Date'
    df['Year'] = pd.to_datetime(df['Application Publication Date'], errors='coerce').dt.year
    df.dropna(subset=['Year', 'Assignee', 'Publication Number'], inplace=True)
    df['Year'] = df['Year'].astype(int)

    # Filter data for years 2010 to 2023
    df = df[(df['Year'] >= 2010) & (df['Year'] <= 2023)].copy()

    # Create base yearly_counts from original CSV data
    yearly_counts = df.groupby(['Assignee', 'Year']).size().reset_index(name='Patents')

    # --- User-provided data for Micron Technology, Inc. ---
    # This data will override the automatically parsed patent counts for Micron
    micron_yearly_applications = {
        2020: 7758, 2021: 6793, 2019: 7284, 2022: 6253, 2018: 6218,
        2006: 5191, 2017: 3632, 2011: 3464, 2013: 2833, 2012: 3054,
        2007: 3472, 2010: 3290, 2014: 2934, 2008: 3674, 2015: 2504,
        2016: 1996, 2009: 3344, 2023: 1964, 2024: 2667, 2025: 205
    }
    # Filter micron_yearly_applications for years 2010 to 2023
    micron_yearly_applications = {year: count for year, count in micron_yearly_applications.items() if 2010 <= year <= 2023}

    # Update yearly_counts for Micron with the provided data
    for index, row in yearly_counts.iterrows():
        if row['Assignee'] == 'Micron Technology, Inc.' and row['Year'] in micron_yearly_applications:
            yearly_counts.loc[index, 'Patents'] = micron_yearly_applications[row['Year']]
    
    # Recalculate Market_Dominance for Micron based on the updated Patents
    micron_cumulative_patents = 0
    for year in sorted(yearly_counts[yearly_counts['Assignee'] == 'Micron Technology, Inc.']['Year'].unique()):
        idx = yearly_counts[(yearly_counts['Assignee'] == 'Micron Technology, Inc.') & (yearly_counts['Year'] == year)].index
        if not idx.empty:
            current_patents = yearly_counts.loc[idx[0], 'Patents']
            micron_cumulative_patents += current_patents
            yearly_counts.loc[idx[0], 'Market_Dominance'] = micron_cumulative_patents
    # --- End of user-provided data handling for Micron ---

    # --- User-provided data for Netapp, Inc. ---
    netapp_yearly_applications = {
        2014: 686, 2008: 377, 2015: 587, 2013: 444, 2007: 339,
        2016: 458, 2006: 372, 2019: 360, 2009: 298, 2022: 335,
        2010: 228, 2020: 261, 2021: 278, 2011: 191, 2017: 313,
        2023: 274, 2012: 206, 2018: 147, 2024: 122, 2025: 21
    }
    # Filter netapp_yearly_applications for years 2010 to 2023
    netapp_yearly_applications = {year: count for year, count in netapp_yearly_applications.items() if 2010 <= year <= 2023}

    # Update yearly_counts for Netapp with the provided data
    for index, row in yearly_counts.iterrows():
        if row['Assignee'] == 'Netapp, Inc.' and row['Year'] in netapp_yearly_applications:
            yearly_counts.loc[index, 'Patents'] = netapp_yearly_applications[row['Year']]
    
    # Recalculate Market_Dominance for Netapp based on the updated Patents
    netapp_cumulative_patents = 0
    for year in sorted(yearly_counts[yearly_counts['Assignee'] == 'Netapp, Inc.']['Year'].unique()):
        idx = yearly_counts[(yearly_counts['Assignee'] == 'Netapp, Inc.') & (yearly_counts['Year'] == year)].index
        if not idx.empty:
            current_patents = yearly_counts.loc[idx[0], 'Patents']
            netapp_cumulative_patents += current_patents
            yearly_counts.loc[idx[0], 'Market_Dominance'] = netapp_cumulative_patents
    # --- End of user-provided data handling for Netapp ---

    # --- User-provided data for Samsung Electronics Co., Ltd. ---
    samsung_yearly_applications = {
        2023: 52617, 2006: 60429, 2022: 56052, 2013: 61962, 2021: 53947,
        2007: 53499, 2014: 59472, 2020: 58644, 2015: 60957, 2012: 49035,
        2008: 43159, 2019: 60919, 2011: 43708, 2018: 55165, 2016: 53768,
        2010: 39228, 2009: 34817, 2017: 50175, 2024: 26479, 2025: 1864
    }
    # Filter samsung_yearly_applications for years 2010 to 2023
    samsung_yearly_applications = {year: count for year, count in samsung_yearly_applications.items() if 2010 <= year <= 2023}

    # Update yearly_counts for Samsung with the provided data
    for index, row in yearly_counts.iterrows():
        if row['Assignee'] == 'Samsung Electronics Co., Ltd.' and row['Year'] in samsung_yearly_applications:
            yearly_counts.loc[index, 'Patents'] = samsung_yearly_applications[row['Year']]
    
    # Recalculate Market_Dominance for Samsung based on the updated Patents
    samsung_cumulative_patents = 0
    for year in sorted(yearly_counts[yearly_counts['Assignee'] == 'Samsung Electronics Co., Ltd.']['Year'].unique()):
        idx = yearly_counts[(yearly_counts['Assignee'] == 'Samsung Electronics Co., Ltd.') & (yearly_counts['Year'] == year)].index
        if not idx.empty:
            current_patents = yearly_counts.loc[idx[0], 'Patents']
            samsung_cumulative_patents += current_patents
            yearly_counts.loc[idx[0], 'Market_Dominance'] = samsung_cumulative_patents
    # --- End of user-provided data handling for Samsung ---

    # --- User-provided data for Sandisk Technologies, Inc. ---
    sandisk_yearly_applications = {
        2023: 53622, 2006: 62531, 2022: 57449, 2013: 63410, 2021: 55588,
        2007: 55893, 2014: 61142, 2020: 60218, 2015: 62528, 2012: 50278,
        2008: 44822, 2019: 62421, 2011: 45074, 2018: 56527, 2016: 54907,
        2010: 40522, 2009: 36446, 2017: 51459, 2024: 26732, 2025: 1869
    }
    # Filter sandisk_yearly_applications for years 2010 to 2023
    sandisk_yearly_applications = {year: count for year, count in sandisk_yearly_applications.items() if 2010 <= year <= 2023}

    # Update yearly_counts for Sandisk with the provided data
    for index, row in yearly_counts.iterrows():
        if row['Assignee'] == 'Sandisk Technologies, Inc.' and row['Year'] in sandisk_yearly_applications:
            yearly_counts.loc[index, 'Patents'] = sandisk_yearly_applications[row['Year']]
    
    # Recalculate Market_Dominance for Sandisk based on the updated Patents
    sandisk_cumulative_patents = 0
    for year in sorted(yearly_counts[yearly_counts['Assignee'] == 'Sandisk Technologies, Inc.']['Year'].unique()):
        idx = yearly_counts[(yearly_counts['Assignee'] == 'Sandisk Technologies, Inc.') & (yearly_counts['Year'] == year)].index
        if not idx.empty:
            current_patents = yearly_counts.loc[idx[0], 'Patents']
            sandisk_cumulative_patents += current_patents
            yearly_counts.loc[idx[0], 'Market_Dominance'] = sandisk_cumulative_patents
    # --- End of user-provided data handling for Sandisk ---

    # --- User-provided data for Sk Hynix Inc. ---
    skhynix_yearly_applications = {
        2008: 8092, 2007: 8420, 2006: 7122, 2009: 5338, 2010: 4734,
        2011: 3745, 2012: 4203, 2020: 4842, 2016: 4462, 2015: 3823,
        2018: 5268, 2019: 5185, 2023: 3297, 2021: 4454, 2014: 3656,
        2022: 3417, 2013: 3107, 2017: 3718, 2024: 1214, 2025: 53
    }
    # Filter skhynix_yearly_applications for years 2010 to 2023
    skhynix_yearly_applications = {year: count for year, count in skhynix_yearly_applications.items() if 2010 <= year <= 2023}

    # Update yearly_counts for Sk Hynix with the provided data
    for index, row in yearly_counts.iterrows():
        if row['Assignee'] == 'Sk Hynix Inc.' and row['Year'] in skhynix_yearly_applications:
            yearly_counts.loc[index, 'Patents'] = skhynix_yearly_applications[row['Year']]
    
    # Recalculate Market_Dominance for Sk Hynix based on the updated Patents
    skhynix_cumulative_patents = 0
    for year in sorted(yearly_counts[yearly_counts['Assignee'] == 'Sk Hynix Inc.']['Year'].unique()):
        idx = yearly_counts[(yearly_counts['Assignee'] == 'Sk Hynix Inc.') & (yearly_counts['Year'] == year)].index
        if not idx.empty:
            current_patents = yearly_counts.loc[idx[0], 'Patents']
            skhynix_cumulative_patents += current_patents
            yearly_counts.loc[idx[0], 'Market_Dominance'] = skhynix_cumulative_patents
    # --- End of user-provided data handling for Sk Hynix ---

    # Get top 5 Assignees based on total patent count (using the potentially updated counts)
    total_patents_per_assignee = yearly_counts.groupby('Assignee')['Patents'].sum().sort_values(ascending=False)
    
    # For debugging: write total patents per assignee to a file
    with open('debug_total_patents.txt', 'w', encoding='utf-8') as f:
        f.write("Total Patents per Assignee (after overrides, before top 5 filter):\n")
        f.write(total_patents_per_assignee.to_string())

    # Re-apply filtering for top 5 after debugging
    top_assignees = total_patents_per_assignee.nlargest(5).index
    filtered_df = yearly_counts[yearly_counts['Assignee'].isin(top_assignees)]

    return filtered_df

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
    assignees = df['Assignee'].unique()
    colors = plt.cm.get_cmap('tab10', len(assignees))
    color_map = {assignee: colors(i) for i, assignee in enumerate(assignees)}

    # Exponential scaling for bubble size
    max_patents = df['Patents'].max()
    # Using a power of 0.5 (square root) for scaling to make smaller bubbles more distinct
    s_multiplier = 2000 / (max_patents**0.5) if max_patents > 0 else 1 

    for assignee in assignees:
        assignee_df = df[df['Assignee'] == assignee].sort_values(by='Year')
        
        # Connect bubbles with lines
        plt.plot(
            assignee_df['Year'],
            assignee_df['Market_Dominance'],
            color=color_map[assignee],
            linestyle='-',
            linewidth=1.5,
            marker='o', # Add marker for each bubble point
            markersize=0, # Hide default marker, will use scatter for custom size
            label=assignee # Label for legend
        )

        # Overlay scatter for custom bubble sizes
        plt.scatter(
            x=assignee_df['Year'],
            y=assignee_df['Market_Dominance'],
            s=assignee_df['Patents']**0.5 * s_multiplier, # Apply exponential scaling
            c=[color_map[assignee]] * len(assignee_df), # Ensure color is applied per point
            alpha=0.7,
            edgecolors="w",
            linewidth=2,
            # No label here, as plot already has it for legend
        )
    
    # --- 4. Chart Title and Labels ---
    plt.title('Patent Portfolio Analysis by Company (Bubble Chart - Top 5 Companies)', fontsize=22, pad=20)
    plt.xlabel('Year', fontsize=16)
    plt.ylabel('Market Dominance (Cumulative Patents)', fontsize=16)
    
    # Set y-axis to logarithmic scale
    plt.yscale('log')
    plt.ylabel('Market Dominance (Cumulative Patents - Log Scale)', fontsize=16)


    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left') # Removed title="Company"
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout(rect=[0, 0, 0.88, 1])
    plt.savefig('./top5_zoned_storage_bubble_chart.png')
    print("top5_zoned_storage_bubble_chart.png 파일 저장 완료.")

def main():
    # 1. 한글 폰트 설정 (attempts to set Korean font, but main labels are English for readability)
    set_korean_font()
    # 2. 데이터 로드 및 전처리
    csv_file_path = '/Users/jichal/cpu 메인 파일/특허 로우 데이터/AB_ Zoned Storage 유지관리 기술의 성능 향상 826 모든 리소스.csv'
    processed_df = load_and_preprocess_data(csv_file_path)
    # 3. 버블 차트 생성
    if not processed_df.empty:
        create_bubble_chart(processed_df)

if __name__ == '__main__':
    main()