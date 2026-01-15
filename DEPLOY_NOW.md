# 🚀 Deploy PeerLens to Render in 10 Minutes

## Quick Start Guide (Recommended Method)

### Step 1: Initialize Git & Push to GitHub (5 minutes)

```bash
cd "/home/shikha/Main/Coding/Prototype 4"

# Initialize git repository
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: PeerLens - Peer Review Synthesis System"

# Create new repository on GitHub
# Go to https://github.com/new
# Repository name: peerlens
# Description: AI-powered peer review synthesis system
# Make it Public or Private
# Don't initialize with README (we already have one)
# Click "Create repository"

# Connect to GitHub (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/peerlens.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Render.com (5 minutes)

1. **Sign up for Render:**
   - Go to https://render.com
   - Click "Get Started"
   - Sign up with GitHub (easiest)

2. **Create New Web Service:**
   - Click "New +" in top right
   - Select "Web Service"
   - Click "Connect Repository"
   - Find and select your `peerlens` repository

3. **Configure Service:**

   **Name:** `peerlens`

   **Root Directory:** `web_ui`

   **Environment:** `Python 3`

   **Build Command:**
   ```bash
   pip install -r requirements.txt && pip install docetl
   ```

   **Start Command:**
   ```bash
   python app.py
   ```

4. **Add Environment Variable:**
   - Scroll down to "Environment Variables"
   - Click "Add Environment Variable"
   - **Key:** `OPENAI_API_KEY`
   - **Value:** `sk-proj-...` (your OpenAI API key)

5. **Deploy:**
   - Click "Create Web Service"
   - Wait 2-3 minutes for deployment
   - Your app will be live at: `https://peerlens.onrender.com`

### Step 3: Test Your Deployment

1. Visit your Render URL
2. Click "Start New Analysis"
3. Select a dataset
4. Configure pipeline
5. Run the synthesis
6. View results!

## ⚡ Even Faster: One Command Deployment

If you want Railway instead (automatic detection):

```bash
# Install Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Login
railway login

# Initialize and deploy
railway init
railway up
railway open
```

That's it! Railway automatically detects Python and deploys.

## 🔑 Important Notes

### Your OpenAI API Key
- **Never commit your `.env` file** (already in `.gitignore`)
- Add it only in the deployment platform's environment variables
- Each platform (Render, Railway, etc.) has a section for env variables

### Free Tier Limits

**Render Free Tier:**
- 750 hours/month
- App sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- ⚠️ Upgrade to $7/month for always-on service

**Railway Free Tier:**
- $5 credit/month
- Good for ~500-1000 pipeline executions
- No sleep time
- Auto-scales

### Making Changes After Deployment

```bash
# Make your code changes locally
git add .
git commit -m "Update: description of changes"
git push

# Render/Railway automatically redeploys!
```

## 🎨 Custom Domain (Optional)

Once deployed, you can add a custom domain:

1. Buy domain (Namecheap, Google Domains, etc.)
2. In Render: Settings → Custom Domain
3. Add your domain
4. Update DNS records (Render provides instructions)
5. Wait for SSL certificate (automatic)

## 📊 Monitoring

**Render Dashboard:**
- View logs
- Monitor performance
- See deployment history
- Restart service if needed

**Railway Dashboard:**
- Real-time logs
- Metrics and analytics
- Easy rollbacks

## ❌ Why Not Vercel?

Vercel is designed for:
- Static sites (Next.js, React)
- Serverless API routes (<60s execution)

PeerLens needs:
- Long-running processes (45-60s pipeline)
- Background jobs
- File system writes
- Subprocess execution

= **Vercel won't work properly** ❌

Use Render or Railway instead ✅

## 🆘 Troubleshooting

### Build Fails
- Check `requirements.txt` is complete
- Ensure Python version compatibility
- Look at build logs in dashboard

### Pipeline Timeouts
- Render free tier may be slower
- Consider upgrading to paid tier
- Check OpenAI API rate limits

### App Not Loading
- Check if service is running (dashboard)
- View logs for errors
- Verify environment variables are set

## 📞 Need Help?

- Render Docs: https://render.com/docs
- Railway Docs: https://docs.railway.app
- Open an issue on GitHub

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Web service configured
- [ ] OpenAI API key added
- [ ] Deployment successful
- [ ] Tested homepage
- [ ] Tested pipeline execution
- [ ] Shared URL with team!

---

**Ready to deploy?** Start with Step 1 above! 🚀
