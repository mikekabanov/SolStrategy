# 📍 Report Navigation Guide - Relative Paths for Cloud Storage

## ✅ All Reports Use Relative Paths

Your HTML reports are now fully **portable** and can be moved to Google Drive, Dropbox, OneDrive, or any other location without breaking navigation links.

---

## 🚀 Quick Start

### Starting Point
Open **`index.html`** in your browser - it's your landing page with links to both reports.

### Navigation Structure
```
index.html (HOME)
    ├─→ report_english.html (English Report)
    │       └─→ [Can navigate to Russian Report or back to Home]
    │
    └─→ report_russian.html (Russian Report)
            └─→ [Can navigate to English Report or back to Home]
```

---

## 📂 How to Upload to Google Drive

1. **Create a folder** on Google Drive (e.g., "SOL-Trading-Reports")
2. **Upload all files** to this folder:
   - `index.html`
   - `report_english.html`
   - `report_russian.html`
   - `data/` folder (with all CSV files and visualizations)
3. **Open `index.html`** in your browser
   - Right-click → "Open with" → "Choose an app" → Select your web browser
   - Or use [HTML Preview](https://htmlpreview.github.io/)

---

## 🔗 What Changed

### Before
```html
<a href="report_russian.html">Russian</a>
<a href="#english">English</a>
```

### After (Now Relative-Safe)
```html
<a href="./report_english.html">English Report</a>
<a href="./report_russian.html">Русский Report</a>
<a href="./index.html" class="home">🏠 Home</a>
```

✨ **All paths use `./filename`** - works anywhere!

---

## 🎯 Navigation Features

Each report page has a top-right navigation bar with:

| Button | Action | Color |
|--------|--------|-------|
| 🏠 Home | Returns to `index.html` | Green |
| English | Opens English report | Blue |
| Русский | Opens Russian report | Blue |

---

## ✨ Key Benefits

✓ **Works on Google Drive** - No special setup needed
✓ **No Broken Links** - All relative paths stay valid
✓ **Offline Capable** - Download and use without internet
✓ **Fully Portable** - Move folder anywhere, links still work
✓ **Mobile Friendly** - Responsive design on all devices
✓ **Cloud Agnostic** - Works on Drive, Dropbox, OneDrive, etc.

---

## 📁 File Organization

Keep files organized like this:
```
Your-Reports-Folder/
├── index.html                    ← Landing page (start here)
├── report_english.html           ← English full report  
├── report_russian.html           ← Russian full report
├── EXPERIMENT_SUMMARY.md         ← Text summary
├── NAVIGATION.md                 ← This file
├── README.md                     ← Project details
└── data/
    ├── signals_pct_3.0_min_120.csv
    ├── backtest_trades.csv
    ├── backtest_threshold_analysis.csv
    ├── feature_correlations.csv
    ├── model_comparison.csv
    ├── experiment_visualizations.png
    └── [other data files]
```

**Important:** All files must stay in the same folder structure for relative paths to work.

---

## 🔍 How Relative Paths Work

When you're viewing `report_english.html` and it contains:
```html
<a href="./index.html">Home</a>
```

The browser finds `index.html` in the **same folder**, regardless of where that folder is:
- Local disk ✓
- Google Drive ✓
- Dropbox ✓
- Web server ✓
- Network drive ✓

---

## 💻 Browser Compatibility

| Browser | Status | Notes |
|---------|--------|-------|
| Chrome | ✓ | Recommended, works everywhere |
| Firefox | ✓ | Works great, responsive design |
| Safari | ✓ | Works on Mac/iOS |
| Edge | ✓ | Windows recommended browser |

---

## ⚠️ Troubleshooting

**Problem:** Links not working
**Solution:** 
- Ensure all `.html` files are in the same folder
- Check file names are exact: `index.html`, `report_english.html`, `report_russian.html`
- Refresh page (Ctrl+F5 or Cmd+Shift+R)

**Problem:** On Google Drive, can't open HTML files
**Solution:** 
- Use [HTML Preview](https://htmlpreview.github.io/) tool
- Or use "Open with" → Chrome from Google Drive context menu
- Or download the folder locally and open locally

**Problem:** Charts/images not displaying
**Solution:** 
- Verify `data/` folder exists in the same directory
- Check that image file names are correct in the `data/` folder
- Clear browser cache

---

## 🎨 Customization Tips

Since paths are relative, you can safely:
- **Rename the folder** - Links still work
- **Move folder** to different location - Links still work
- **Share via cloud** - Everyone can navigate smoothly
- **Edit HTML** - Modify content without breaking links
- **Add files** - Add new files to `data/` folder, update HTML links

---

## 📱 Mobile & Tablet

Reports are fully responsive:
- Open on smartphone ✓
- Open on tablet ✓
- Open on desktop ✓
- All navigation works on touch devices ✓

---

## 🔐 Privacy & Security

- No external scripts or CDN dependencies
- No analytics or tracking
- Works completely offline
- No data sent to any servers
- Fully self-contained HTML files

---

## 📊 Report Access

### Landing Page Navigation
```
index.html
├── Statistics Dashboard (49.44% return, 98.4% win rate, etc.)
├── Quick Links to Reports
├── File Inventory
├── Data Files Description
└── Strategy Approval Status
```

### English Report Structure
```
report_english.html
├── Executive Summary
├── Step 1: Data Preparation
├── Step 2: ML Development
├── Step 3: Backtesting
├── Visualizations
├── Key Findings
├── Recommendations
└── Technical Appendix
```

### Russian Report Structure
```
report_russian.html
├── Резюме
├── Шаг 1: Подготовка данных
├── Шаг 2: Разработка ML
├── Шаг 3: Тестирование
├── Визуализации
├── Выводы
├── Рекомендации
└── Технический раздел
```

---

## 📞 Quick Links

- **Start Here:** Open `index.html` in your browser
- **English Full Report:** `report_english.html`
- **Russian Full Report:** `report_russian.html`
- **Text Summary:** `EXPERIMENT_SUMMARY.md`
- **Project Details:** `README.md`

---

**Updated:** March 17, 2026  
**Status:** ✅ All links use relative paths  
**Portability:** 🌍 Works anywhere, any platform  
**Verified:** ✓ Tested for Google Drive compatibility
