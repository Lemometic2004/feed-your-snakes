# 🐍 Snake Feeding Log System (Python + CLI + Charts)

A simple, local record system for snake feeding logs — written in **Python**, with a **Windows Batch Menu**, **CSV storage**, and **chart + Excel export**.

🇨🇳 **简介：**  
这是一个用 Python 编写的蛇类喂食记录系统，  
可通过命令行菜单添加、查看、导出喂食数据，并自动生成图表。

---

```markdown
## 📦 Project Structure
feed_your_snakes.py # Core logic (record, export, visualize)
feed_your_snakes.bat # CLI menu for one-click operation
data/snake_feedings.csv # Feeding data storage
charts/ # Auto-generated charts
```

---

## 🧰 Features
✅ Add feeding records interactively  
✅ View last 20 feeding logs  
✅ Generate feeding charts (Matplotlib)  
✅ Export to Excel (`.xlsx`, via XlsxWriter)  
✅ Backup before clearing data  

---

## ⚙️ Requirements
Install once before running:
```bash
pip install pandas matplotlib xlsxwriter
```

## 🚀 How to Run

Double-click feed_your_snakes.bat

Choose from the menu:

1) Add feeding record
2) View recent records
3) Generate charts
4) Export Excel
5) Clear data (with backup)
6) Open data folder
7) Exit


All CSV data is stored in data/snake_feedings.csv.

🐍 Author
ChatGPT & Lemometic
Designed with ❤️ for reptile lovers and data-keepers.