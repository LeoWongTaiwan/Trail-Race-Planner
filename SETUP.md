# Trail Planner 自動更新 V1

## 這一版已經自動化什麼

- 每週一自動執行。
- 搜尋視窗永遠維持「執行當天起往後 365 天」。
- 報名截止日已過，自動改為 closed。
- 尚未開放，自動改為 soon。
- 無法確認日期的資料只會標成 pending，不會錯誤標成可報名。
- 更新完成後自動 Commit 到 GitHub。
- Netlify 已連接 GitHub，因此會自動重新部署。

## 這一版尚未自動化什麼

- 尚未自動發現所有新賽事。
- 尚未自動讀取微信公眾號或小程序。
- UTMB、ITRA 和公開平台的抓取器會在後續逐一加入。

這樣安排是為了先確保狀態不會過期，也不會把不確定資料錯誤標成可報名。

## 第一次安裝

把這個 zip 解壓縮後，將所有檔案與資料夾上傳到 GitHub repository 根目錄並 Commit。

上傳後應看到：

- index.html
- manifest.json
- icon-192.png
- icon-512.png
- data/
- scripts/
- .github/

## 測試自動更新

GitHub repository → Actions → Weekly Trail Planner Update → Run workflow。

如果成功，data/races.json 的 lastUpdated 會變更，Netlify 會自動部署。
