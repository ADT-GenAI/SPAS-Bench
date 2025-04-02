import pandas as pd
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

# 設定繁體中文
matplotlib.rcParams['font.family'] = 'Microsoft JhengHei'  # Windows 微軟正黑體
matplotlib.rcParams['axes.unicode_minus'] = False  # 正確顯示負號

# 模型尺寸資料
MODEL_SIZE = {
    "GPT-4o": 175, "GPT-4.5-Preview": 175, "Claude-3.5-Sonnet": 175, "Claude-3.5-Haiku": 175, "Claude-3.7": 175, "Gemini-2.0-Flash": 137, "Grok-2": 175,
    "Gemma-3-27B": 27, "LLaMA Taiwan 70B": 70, "LLaMA-Taide-7B": 7, "LLaMA 3": 70, "Mixtral 8x22B": 176
}

# 載入所有 SPAS_results_開頭的檔案
def load_all_results(folder: str) -> pd.DataFrame:
    all_dfs = []
    for file in os.listdir(folder):
        if file.startswith("SPAS_results_") and file.endswith(".csv"):
            df = pd.read_csv(os.path.join(folder, file), encoding='utf-8-sig')
            all_dfs.append(df)
    combined = pd.concat(all_dfs, ignore_index=True)
    print(f"[INFO] 已合併 {len(all_dfs)} 個模型結果，共 {len(combined)} 答案")
    return combined

# 圖一：模型尺寸 vs 總正確率
def plot_overall_accuracy(results: pd.DataFrame, output_path_spots: str = "spots.png"):
    color_map = {
        'GPT-4o': '#1f77b4',
        'GPT-4.5-Preview': '#34495E',
        'Claude-3.5-Sonnet': '#839192',
        'Gemini-2.0-Flash': '#17becf',
        'Grok-2': '#5DADE2',
        'Gemma-3-27B': '#E67E22',
        'LLaMA-Taide-7B': '#FF6F61',
    }
    summary = results.groupby('模型')['正確'].mean().reset_index()
    summary['模型尺寸'] = summary['模型'].map(MODEL_SIZE)
    plt.figure(figsize=(9, 7))
    for _, row in summary.iterrows():
        model = row['模型']
        size = row['模型尺寸']
        acc = row['正確'] * 100
        color = color_map.get(model, 'gray')
        plt.scatter(size, acc, s=100, color=color)
        plt.annotate(model, (size, acc), textcoords="offset points", xytext=(8,1), ha='left', fontsize=8)
    plt.xlabel("模型參數規模 (B)")
    plt.ylabel("總正確率 (%)")
    plt.title("模型尺寸 vs 總成績")
    plt.tight_layout()
    plt.savefig(output_path_spots, dpi=300, bbox_inches='tight')
    print(f"[INFO] 圖片已儲存至 {output_path_spots}")
    plt.show()

# 圖二：各模型在一級分類表現
def plot_category_accuracy(results: pd.DataFrame, output_path_bar: str = "bar.png"):
    grouped = results.groupby(['模型', '一級類別'])['正確'].mean().unstack()
    desired_order = ['製造基礎能力', '製造知識處理與決策', '製造智慧應用']
    grouped = grouped[desired_order]
    colors = ['#839192', '#5DADE2', '#E67E22']  # 鐵灰 → 天藍 → 橘
    ax = grouped.plot(kind='bar', figsize=(12, 6), color=colors)
    plt.ylabel("正確率 (%)")
    plt.title("模型在一級類別的表現")
    plt.xticks(rotation=0)
    plt.legend(title="一級類別", bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    for container in ax.containers:
        labels = [f"{v.get_height() * 100:.1f}%" for v in container]
        ax.bar_label(container, labels=labels, padding=3, fontsize=8)
    plt.tight_layout()
    plt.savefig(output_path_bar, dpi=300, bbox_inches='tight')
    print(f"[INFO] 圖片已儲存至 {output_path_bar}")
    plt.show()

# 圖三：二級類別雷達圖
def plot_radar_chart(results: pd.DataFrame, output_path_rader: str = "radar.png"):
    grouped = results.groupby(['模型', '二級類別'])['正確'].mean().unstack().fillna(0)
    labels = grouped.columns.tolist()
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    closed_models = ["GPT-4o", "GPT-4.5-Preview", "Claude-3.5-Sonnet", "Claude-3.5-Haiku", "Claude 3.7", "Gemini-2.0-Flash", "Grok-2"]
    open_models = ["Gemma-3-27B", "LLaMA-3-70B", "LLaMA-Taiwan-70B", "Mixtral-7x22", "LLaMA-Taide-7B"]
    color_map = {
        'GPT-4o': '#1f77b4',           # deep blue（閉源）
        "GPT-4.5-Preview": '#34495E',  # soft navy（閉源）
        'Claude 3.5': '#2ca02c',       # steel blue（閉源）
        'Gemini-2.0-Flash': '#17becf', # ocean blue（閉源）
        'Grok-2': '#5DADE2',           # sky blue（閉源）
        'Gemma-3-27B': '#E67E22',       # hot orange（開源）
        'LLaMA-Taide-7B': '#FF6F61',      # strong coral（開源）
    }
    plt.figure(figsize=(10, 6))
    ax = plt.subplot(111, polar=True)
    for name, row in grouped.iterrows():
        values = row.tolist()
        values += values[:1]
        color = color_map.get(name, 'gray')
        linestyle = '-' if name in closed_models else '--'  # 閉源實線，開源虛線
        ax.plot(angles, values, linewidth=2, label=name, color=color, linestyle=linestyle)
        ax.fill(angles, values, alpha=0.1, color=color)
    plt.xticks(angles[:-1], labels, fontsize=10)
    plt.yticks([0.2, 0.4, 0.6, 0.8, 1.0], ["20%", "40%", "60%", "80%", "100%"], fontsize=9)
    plt.title("模型在二級能力的表現", size=14)
    plt.legend(loc='center left', bbox_to_anchor=(1.2, 0.5), borderaxespad=0., fontsize=10, title="模型名稱")
    plt.tight_layout()
    plt.savefig(output_path_rader, dpi=300, bbox_inches='tight')
    print(f"[INFO] 圖片已儲存至 {output_path_rader}")
    plt.show()


# main
if __name__ == "__main__":
    result_folder = r"C:\Users\DT25006\OneDrive - AUO DIGITECH PTE LTD\QIA Team\SPAS腳本\Results"
    df_combined = load_all_results(result_folder)
    plot_overall_accuracy(df_combined)
    plot_category_accuracy(df_combined)
    plot_radar_chart(df_combined)



