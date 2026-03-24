# 跳棋遊戲（mac 免安裝版，含電腦對戰）

你剛剛遇到的 `macOS 26 ... required` 是執行環境相容問題。  
我改成 **瀏覽器版**，不需要 Python/Tk，mac 直接可玩。

## 啟動方式

1. 在 Finder 進入此資料夾。  
2. 雙擊 `checkers_web.html`（或右鍵用 Safari / Chrome 開啟）。

## 遊戲規則（已實作）

- 玩家紅方先手，電腦黑方。
- 強制吃子。
- 可連跳時必須繼續跳。
- 到底線會升王（K）。
- 可按「重新開始」。

## 檔案

- `checkers_web.html`：主程式（推薦使用）
- `checkers_game.py`：舊版 Python/Tk 版本（你的系統可能不相容）
