# 📋 Deployment Quick Reference Card

## Print This & Use While Deploying

---

## 🎯 3 Deployment Paths (Choose One)

### PATH 1️⃣: GitHub Pages (Recommended - 10 min)
```
✅ Free, permanent, professional
✅ HTTPS automatic
✅ Easy updates
✅ Works on all devices

1. github.com/new → name: SolStrategy → Public → Create
2. cd c:\data\SolStrategy
3. git init && git add . && git commit -m "initial"
4. git remote add origin https://github.com/USERNAME/SolStrategy.git
5. git branch -M main && git push -u origin main
6. Settings → Pages → main / → Save
7. Wait 1-2 minutes
8. View: https://USERNAME.github.io/SolStrategy
```

### PATH 2️⃣: Netlify (Easiest - 2 min)
```
✅ Drag & drop
✅ Auto deploys
✅ Perfect for beginners

1. netlify.com
2. Drag-drop SolStrategy folder
3. Wait 30 seconds
4. View: https://[random-name].netlify.app
```

### PATH 3️⃣: Google Drive (Instant - 1 min)
```
✅ No setup
✅ Works immediately
✅ Just share link

1. Upload SolStrategy folder to Google Drive
2. Right-click any .html → Open with → Chrome
3. Share folder link
```

---

## 🚨 Troubleshooting

| Problem | Solution | Time |
|---------|----------|------|
| "Page not found" (404) | Wait 1-2 min, hard refresh (Ctrl+Shift+R) | 2 min |
| Links broken | Use ./ paths (./report_english.html) | 5 min |
| Can't push to GitHub | Check username/password, try `git status` | 5 min |
| GitHub Pages not showing | Check Settings → Pages has green checkmark | 3 min |
| Files not on GitHub | Check `git push` completed successfully | 5 min |

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] GitHub account (free)
- [ ] Git installed (`git --version`)
- [ ] Currently in c:\data\SolStrategy folder

### Step 1: Create Repository (2 min)
- [ ] Go to github.com/new
- [ ] Name: SolStrategy
- [ ] Public (not private)
- [ ] Create (do NOT initialize with README)
- [ ] Copy URL: https://github.com/USERNAME/SolStrategy.git

### Step 2: Configure Git (2 min)
- [ ] `git config --global user.email "your.email@example.com"`
- [ ] `git config --global user.name "Your Name"`
- [ ] Verify: `git config --global user.email`

### Step 3: Push Files (3 min)
- [ ] `git init`
- [ ] `git add .`
- [ ] `git commit -m "Initial commit"`
- [ ] `git remote add origin https://github.com/USERNAME/SolStrategy.git`
- [ ] `git branch -M main`
- [ ] `git push -u origin main`

### Step 4: Enable GitHub Pages (1 min)
- [ ] Go to your GitHub repo
- [ ] Settings → Pages
- [ ] Deploy from branch → main → /
- [ ] Save

### Step 5: Verify (2 min)
- [ ] Wait 1-2 minutes
- [ ] Visit: https://USERNAME.github.io/SolStrategy
- [ ] Should show landing page ✓
- [ ] Test English report link ✓
- [ ] Test Russian report link ✓
- [ ] Test on mobile ✓

### Step 6: Share (1 min)
- [ ] Copy URL: https://USERNAME.github.io/SolStrategy
- [ ] Send to colleagues
- [ ] Done! ✅

---

## 📚 3 Essential Guides

| Guide | Time | When |
|-------|------|------|
| [**QUICK_START.md**](./QUICK_START.md) | 5 min | First time, just commands |
| [**DEPLOYMENT_CHECKLIST.md**](./DEPLOYMENT_CHECKLIST.md) | 15 min | Step-by-step with details |
| [**GITHUB_DEPLOYMENT.md**](./GITHUB_DEPLOYMENT.md) | 30 min | Full guide + troubleshooting |

---

## 🔗 Key URLs

| Purpose | URL |
|---------|-----|
| Create Repository | https://github.com/new |
| View Your Repo | https://github.com/USERNAME/SolStrategy |
| Enable Pages | https://github.com/USERNAME/SolStrategy/settings/pages |
| Live Report | https://USERNAME.github.io/SolStrategy |
| English Report | https://USERNAME.github.io/SolStrategy/report_english.html |
| Russian Report | https://USERNAME.github.io/SolStrategy/report_russian.html |

---

## 🐍 Git Commands Reference

```bash
# One-time setup
git config --global user.email "you@example.com"
git config --global user.name "Your Name"

# Initialize new repo
git init

# Add files
git add .              # Add all files
git add *.html         # Add only specific files
git status             # See what will be added

# Commit & Push
git commit -m "Initial commit"  # Save to local
git remote add origin https://...  # Point to GitHub
git branch -M main     # Rename to main
git push -u origin main  # Upload to GitHub

# Future updates
git add .
git commit -m "Update reports"
git push origin main
```

---

## 📊 File Structure After Push

```
Your GitHub Repo
├── index.html                    ← Landing page
├── report_english.html           ← Full report
├── report_russian.html           ← Full report
├── QUICK_START.md               ← Deployment guide
├── DEPLOYMENT_CHECKLIST.md      ← Step-by-step
├── GITHUB_DEPLOYMENT.md         ← Detailed guide
├── PROJECT_SUMMARY.md           ← Overview
├── .gitignore                   ← Git configuration
├── _config.yml                  ← GitHub Pages config
└── data/                        ← CSV files
    ├── signals_pct_3.0_min_120.csv
    ├── backtest_trades.csv
    └── [other CSV files]
```

---

## 💡 Pro Tips

✅ **Use HTTPS clone URL** (not SSH)  
✅ **Make repository PUBLIC** (not private)  
✅ **Wait 1-2 minutes** for GitHub Pages to build  
✅ **Hard refresh** with Ctrl+Shift+R if cached  
✅ **Share the .github.io URL** not the repo URL  
✅ **HTML files must be in root** (not subdirectory)  
✅ **Check Settings → Pages** to verify it built  

---

## 🎯 What You're Watching For

### GitHub Repository
✅ Files appear on github.com  
✅ Shows your username/SolStrategy  
✅ Lists all HTML and CSV files  

### GitHub Pages
✅ Settings → Pages shows "Your site is live at..."  
✅ Green checkmark appears  
✅ URL format: https://USERNAME.github.io/SolStrategy  

### Live Report
✅ Page loads in under 2 seconds  
✅ All links work (navigation, language switcher)  
✅ CSV files available for download  
✅ Looks good on mobile  

---

## ⏱️ Time Estimates

| Task | Time | Difficulty |
|------|------|-----------|
| Create GitHub account | 2 min | Very Easy |
| Install Git | 5 min | Easy |
| Create repository | 2 min | Very Easy |
| Push files (git) | 3 min | Easy |
| Enable GitHub Pages | 1 min | Very Easy |
| Wait for build | 1-2 min | N/A |
| **TOTAL** | **~15 min** | **Easy** |

---

## 🆘 Quick Troubleshooting

**Q: I see "Page not found"**  
A: Wait 1-2 minutes and hard refresh (Ctrl+Shift+R)

**Q: Settings → Pages is grayed out**  
A: Repository must be PUBLIC (check Settings → General)

**Q: Git says "401 unauthorized"**  
A: Use correct username, create GitHub token if using 2FA

**Q: Files didn't upload**  
A: Check `git push` message, should say "main -> main"

**Q: Links between reports broken**  
A: All links use ./filename.html (they should work)

**Q: Takes too long to load**  
A: First load can be slow (1st visits), then cached

---

## 📱 Mobile Testing

After deployment, test on phone:
```
1. Open Safari/Chrome on phone
2. Visit: https://USERNAME.github.io/SolStrategy
3. Check:
   - Landing page displays
   - Can tap on report links
   - Can switch language
   - Can download files
   - Text is readable (not too small)
```

---

## 🎉 Success Checklist

- [ ] Can access https://USERNAME.github.io/SolStrategy
- [ ] All 3 pages load without errors
- [ ] Can switch languages
- [ ] Can view on mobile
- [ ] Friends can access (send them link)
- [ ] GitHub repo shows all files
- [ ] CSV files downloadable
- [ ] HTTPS lock shows (secure)

---

## 📞 Need Help?

1. **Check** [QUICK_START.md](./QUICK_START.md)
2. **See** [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
3. **Read** [GITHUB_DEPLOYMENT.md](./GITHUB_DEPLOYMENT.md)
4. **Visit** https://pages.github.com (official help)
5. **Check** Settings → Pages (error messages)

---

## ✨ Final Notes

✅ This is the easiest part of the whole project  
✅ GitHub Pages is reliable and free  
✅ Takes 10-15 minutes total  
✅ Updates are 1-minute (just git push)  
✅ Your reports will be online forever  
✅ Colleagues can access 24/7  
✅ No servers to manage  
✅ No costs whatsoever  

---

## 🚀 YOU'VE GOT THIS!

**Start Here**: [QUICK_START.md](./QUICK_START.md)  
**Questions**: See [GITHUB_DEPLOYMENT.md](./GITHUB_DEPLOYMENT.md)  
**Step-by-Step**: [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)  

**Ready?** Let's go! 🎉

---

**Pro Tips Reminder:**
- 🔵 Circle your chosen deployment path (GitHub/Netlify/Drive)
- 📝 Write down your GitHub username
- ⏰ Block 15 minutes (don't rush)
- 💬 Message colleagues once live
- ✅ Celebrate when it's working!

---

**Generated**: March 17, 2026  
**Print This**: Yes  
**Bookmark This**: Yes  
**Share This**: With your team

🎯 **TARGET**: Live in 15 minutes or less
