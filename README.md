# 海面之下 — Geomni Day08 / Utopia

北臺灣至北方三島的船隻透視地圖。此儲存庫保存本機 v13 版本，包含執行所需的預處理資料。

## 執行

```sh
python3 -m http.server 8781 --bind 127.0.0.1
```

開啟 `http://127.0.0.1:8781/`。前端為靜態 HTML / Canvas / JavaScript，不需要 Node 安裝或資料 API 金鑰。

- 左側選擇參考點；拖曳海面平移地圖、抓住船拖曳改變船位。
- 滾輪以游標位置縮放；圖內按鈕縮放或回到船位。
- 透視半徑 500–2,000 m；20 m 等深線，四島陸地持續顯示。
- 右側提供格網水深、可收合剖面、TBIA 歷史紀錄及來源明細。

## 資料與存取範圍

依使用者2026-11-09明確要求，此儲存庫設為 **public**；未啟用 GitHub Pages，未自動發布 Facebook。

GEBCO 2024 海底地形、農業部人工礁、TBIA 多來源魚類資料、使用者提供的四島 Shapefile 與參考點，均保留各自來源與限制。沒有對全部資料授予統一授權。四島圖資由使用者確認下載自[政府資料開放平臺](https://data.gov.tw/)，屬開放資料；具體資料集頁、發布機關、版本與授權條款連結尚待補齊，未自行推定特定授權版本。原始Shapefile的PRJ與雜湊已保存。

TBIA 的 CC BY、CC BY-NC、CC0、OGDL 等授權按來源保存在 `data/tbia-data.js`；未使用外部魚類照片。8 km 誤差、模糊化敏感位置、未驗證館藏等資料不混入局部魚種清單。點位不等於當下魚群或完整棲地。

詳見 [資料處理說明](TBIA-NOTES.txt)、[島嶼檢核](evidence/islands-qa.json) 和 [互動驗收](evidence/v13-qa.json)。`evidence/layout-v13.png` 是本機實際瀏覽器截圖。

## 重現與原件

現有地圖可以直接執行，不需重跑資料前處理。`scripts/` 保存下載、處理及檢核程式；Python環境版本見 `evidence/environment.json`。

原始 ZIP、PDF、完整 TBIA 匯出和歷代截圖未上傳。完整資料重建需將使用者的 TBIA ZIP／欄位說明及 north_island.zip 放回原腳本指定的 `data/raw/` 目錄，並取回下載來源；不能把即時重新下載宣稱為相同歷史快照。原始檔雜湊保存在 QA 中。

順序：下載來源 → `build.py` → `process-tbia.py` → `contours-20m.py` → `integrate-islands.py`。其中 `build.py` 依賴舊 TaiBIF 原始快照來重建基底；本版魚類顯示由 TBIA 取代，不相加。上傳包的來源檔案對照見 `PACKAGE-MANIFEST.json`。

公開儲存庫已獲使用者授權；Facebook文章仍未獲發布批准。
