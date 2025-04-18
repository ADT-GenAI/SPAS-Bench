在SPAS Benchmark中， 完整題庫與`sample_questions.json`的欄位定義與格式如下：

| 欄位名稱   | 資料型別  | 說明 |
|------------|--------|------|
| 一級類別   | 字串     | 表示題目對應的製造業能力層級，從基礎到進階分別為：製造基礎能力、製造知識處理與決策、製造智慧應用。每個類別對應不同層次的認知、知識量與推理需求。 |
| 二級類別   | 字串     | 為各能力層級中對應的模型能力細分類，例如：知識問答、數學計算、資訊搜索、複雜推理決策等，反映模型需具備的處理技能。 |
| 主題       | 字串     | 題目的具體主題或應用領域，可用於後續分析模型的知識涵蓋。 |
| 難易       | 字串     | 題目的難易度等級，分為易、中、難，可用於後續分析模型的作答情況。 |
| 題目       | 字串     | 題目內容，包含文字、表格、數據等格式，為四選一或二選一選擇題，使用 (A)(B)(C)(D) 標示。 |
| 解答       | 字串     | 正確答案的標示，以A、B、C、D 標示。 |
