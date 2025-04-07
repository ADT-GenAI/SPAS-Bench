# SPAS-Bench: Smart Production Agents System Benchmark
SPAS-Bench 是一個針對智慧製造場域設計的大型語言模型基準資料集，涵蓋製造業需求的基礎能力、知識處理與決策、智慧應用三大類能力，並細分九個次級任務。其目標是促進語言模型在製造領域的真實應用能力評估。

## Introduction
本基準涵蓋三大能力面向：
- 製造基礎能力（數學計算、知識問答、文字理解與生成）
- 製造知識處理與決策（資訊搜索、知識庫檢索、複雜推理決策）
- 製造智慧應用（生產管理、能耗管理、永續管理）

SPAS 的測試資料包括：
- 選擇題、是非題、數值計算題
- 題庫以 `JSON` 格式儲存，包含題目 ID、分類、正確解答與提示資料
- 每個任務都明確對應工廠場景的實際需求

## Evaluation Results
以下為幾項開源和閉源主要模型在不同能力層級的表現：

- 模型總體表現 vs 模型大小
![Scatter](images/spots.png)

- 模型在一級分類的表現（Bar Chart）
![Bar](images/bar.png)

- 模型在二級能力的表現（Radar Chart）
![Radar](images/radar.png)

- 完整的正確率資料：
[`score.csv`](./score.csv)

## Usage
Step1: 聯繫作者並Clone 本專案: git clone https://github.com/ADT-GenAI/SPAS-Bench.git
 
Step2: 載入作者提供的questions.json 作模型測試

Step3: 透過 score.csv 比較模型成績

若您在使用過程中有任何問題或建議，請開啟 Issue 或聯絡我們。
