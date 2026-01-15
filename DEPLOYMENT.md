# PeerLens Deployment Guide

## ⚠️ Important: Vercel Limitations

**Vercel is NOT recommended for this application** due to the following constraints:

### Why Vercel Won't Work Well:

1. **Serverless Timeout Limits**
   - Vercel serverless functions: 10s default, 60s max (Pro plan)
   - Pipeline execution: 45-60 seconds needed
   - ❌ Pipeline will timeout before completing

2. **No Background Processing**
   - Vercel doesn't support long-running background threads
   - Our pipeline runs in a background thread
   - ❌ Real-time pipeline execution won't work

3. **File System Limitations**
   - Vercel serverless functions have read-only file systems
   - Pipeline needs to write output files
   - ❌ Can't save generated briefs

4. **Subprocess Restrictions**
   - DocETL runs as a subprocess command
   - Limited subprocess support in serverless
   - ❌ `docetl run` command may fail

## ✅ Recommended Deployment Platforms

### Option 1: Render.com (Recommended)
**Best for this application**

**Pros:**
- ✓ Full Python support with long-running processes
- ✓ Free tier available
- ✓ Persistent file storage
- ✓ Easy deployment from GitHub
- ✓ Background workers supported

**Steps:**
1. Push code to GitHub
2. Go to https://render.com
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Build Command:** `pip install -r web_ui/requirements.txt && pip install docetl`
   - **Start Command:** `cd web_ui && python app.py`
   - **Environment:** Python 3
6. Add environment variable: `OPENAI_API_KEY=your_key_here`
7. Deploy!

### Option 2: Railway.app
**Modern platform with great DX**

**Pros:**
- ✓ Automatic deployments from Git
- ✓ Free $5/month credit
- ✓ Supports long-running processes
- ✓ Environment variables easy to manage

**Steps:**
1. Push code to GitHub
2. Go to https://railway.app
3. Click "New Project" → "Deploy from GitHub"
4. Select your repository
5. Railway auto-detects Python
6. Add environment variable: `OPENAI_API_KEY`
7. Deploy!

### Option 3: DigitalOcean App Platform
**Reliable and scalable**

**Pros:**
- ✓ $5/month basic plan
- ✓ Full app hosting
- ✓ Auto-scaling capabilities

**Steps:**
1. Push to GitHub
2. Go to https://cloud.digitalocean.com/apps
3. Create new app from GitHub
4. Configure Python app
5. Add environment variables
6. Deploy!

### Option 4: Traditional VPS (Most Control)
**AWS EC2, DigitalOcean Droplet, Linode**

**Pros:**
- ✓ Full control
- ✓ No restrictions
- ✓ Can install anything

**Basic Setup:**
```bash
# SSH into your server
ssh user@your-server-ip

# Install dependencies
sudo apt update
sudo apt install python3 python3-pip

# Clone your repository
git clone your-repo-url
cd Prototype\ 4

# Install dependencies
pip3 install -r web_ui/requirements.txt
pip3 install docetl

# Set environment variable
export OPENAI_API_KEY=your_key_here

# Run with production server
cd web_ui
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 🔧 If You MUST Use Vercel (Limited Functionality)

You can deploy to Vercel for **demo/UI purposes only**, but pipeline execution won't work.

### What Will Work:
- ✓ Static pages (homepage, data selection, configuration)
- ✓ Viewing pre-generated results
- ✓ UI/UX demonstration

### What Won't Work:
- ❌ Running the pipeline
- ❌ Generating new briefs
- ❌ Real-time processing

### Vercel Deployment Steps:

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy from web_ui directory:**
   ```bash
   cd web_ui
   vercel
   ```

4. **Follow prompts:**
   - Set up project? Yes
   - Project name: peerlens
   - Directory: ./
   - Override settings? No

5. **Deploy:**
   ```bash
   vercel --prod
   ```

### Vercel Configuration (Already Created)
`vercel.json` has been created in `web_ui/` directory with basic Flask configuration.

## 📦 Pre-Deployment Checklist

Before deploying to any platform:

- [ ] Push code to GitHub
- [ ] Add `.env` file to `.gitignore` (already done)
- [ ] Have your OpenAI API key ready
- [ ] Test locally one more time
- [ ] Update `requirements.txt` if needed
- [ ] Choose deployment platform
- [ ] Configure environment variables on platform
- [ ] Test deployment after going live

## 🔐 Environment Variables Needed

On your deployment platform, set:
```
OPENAI_API_KEY=sk-proj-your-key-here
```

## 📊 Post-Deployment Testing

After deployment, test:
1. Homepage loads correctly
2. Navigation works
3. Static assets (CSS, JS) load
4. Can view existing results (if any)
5. Pipeline execution (if supported by platform)

## 🆘 Troubleshooting

### "Module not found" errors
- Ensure all dependencies are in `requirements.txt`
- Check Python version compatibility

### Pipeline times out
- Use a platform with longer timeouts (not Vercel)
- Consider Render, Railway, or VPS

### File write errors
- Platform may have read-only filesystem
- Use platforms with persistent storage

## 📞 Support

For deployment issues:
- Render: https://render.com/docs
- Railway: https://docs.railway.app
- DigitalOcean: https://docs.digitalocean.com/products/app-platform/

## 🎯 Recommendation Summary

| Platform | Best For | Pipeline Support | Cost |
|----------|----------|------------------|------|
| **Render** ⭐ | Full functionality | ✅ Yes | Free tier available |
| Railway | Modern deployment | ✅ Yes | $5/month credit |
| DigitalOcean | Production apps | ✅ Yes | $5/month |
| VPS | Maximum control | ✅ Yes | $5-10/month |
| Vercel | Static demo only | ❌ No | Free tier available |

**Bottom line:** Use **Render.com** for easiest deployment with full functionality.
