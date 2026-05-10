# Deploy to Streamlit Cloud

## 🚀 Quick Deploy Steps

### 1. Push to GitHub
```powershell
# Make sure you're in the project directory
cd c:\Users\tomoh.ikfingeh\green-supply-chain-auditor

# Check your git status
git status

# Add all files (except .env - already in .gitignore)
git add .
git commit -m "Ready for Streamlit Cloud deployment"
git push origin main
```

### 2. Deploy on Streamlit Cloud

1. **Go to:** https://share.streamlit.io/
2. **Sign in** with GitHub
3. **Click:** "New app"
4. **Fill in:**
   - Repository: `ImmortalDreamX50/green-supply-chain-auditor`
   - Branch: `main`
   - Main file path: `app.py`

5. **Add Secrets** (Click "Advanced settings" → "Secrets"):
   ```toml
   OPENAI_API_KEY = "your-openai-api-key-here"
   CREWAI_VERBOSE = "false"
   ```

6. **Click:** "Deploy!"

---

## ⚠️ IMPORTANT: Fix API First

Your OpenAI API key has **no credits**. Before deploying:

### Option A: Add Credits (5 minutes)
1. Go to: https://platform.openai.com/settings/organization/billing
2. Add $5-10
3. Test locally: `python agents.py`
4. Then deploy

### Option B: Get AMD API (Recommended for Hackathon)
1. Request AMD Developer Cloud access
2. Update secrets with AMD credentials
3. Update agents.py to use AMD model

---

## 📊 Your Live URLs

After deployment, you'll get:
- **Public URL:** `https://yourapp.streamlit.app`
- **Share with team:** Anyone can access without login!

---

## 🔄 Update Your Deployed App

After pushing changes to GitHub:
```powershell
git add .
git commit -m "Updated features"
git push
```

Streamlit Cloud auto-redeploys in ~1 minute!

---

## ✅ Checklist Before Sharing

- [ ] Fix API credits/access
- [ ] Test locally: `python agents.py` works
- [ ] Test Streamlit: Upload sample_shipments.csv
- [ ] Push to GitHub
- [ ] Deploy to Streamlit Cloud
- [ ] Add API secrets in cloud
- [ ] Test live URL
- [ ] Share with team! 🎉

---

## 💡 Tips

1. **Free Tier:** Streamlit Cloud is FREE for public repos!
2. **Performance:** ChromaDB works perfectly in the cloud
3. **Logs:** Check app logs in Streamlit Cloud dashboard
4. **Custom Domain:** Available on paid plans

---

## 🆘 If Deployment Fails

**Common issues:**
- **"Module not found"** → Check requirements.txt
- **"API error"** → Check secrets configuration
- **"Memory error"** → ChromaDB loads fine, just takes 30s first time

**Need help?** Check: https://docs.streamlit.io/deploy
