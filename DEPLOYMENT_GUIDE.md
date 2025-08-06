# 🚀 ContentStrategist Deployment Guide

## Deploy to Render (Recommended)

### Step 1: Prerequisites
- GitHub account with this repository
- Render account (free at render.com)

### Step 2: Environment Variables
You'll need these environment variables in Render:

```
OPENAI_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_BUCKET=your_supabase_storage_bucket_name
SECRET_KEY=your_flask_secret_key
```

### Step 3: Deploy to Render

1. **Go to Render Dashboard**
   - Visit https://render.com
   - Sign up/Login with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select `ContentStrategist` repository

3. **Configure Service**
   - **Name:** `contentstrategist` (or your preferred name)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -c gunicorn.conf.py app:app`
   - **Plan:** Select "Free" (for testing)

4. **Add Environment Variables**
   - Go to "Environment" tab
   - Add all the environment variables listed above
   - **Important:** Use your actual API keys and Supabase credentials

5. **Deploy**
   - Click "Create Web Service"
   - Wait for build and deployment (5-10 minutes)
   - Your app will be available at: `https://your-app-name.onrender.com`

### Step 4: Test Your Deployment
1. Visit your Render URL
2. Try generating a calendar for any month
3. Verify Excel download works

## Alternative Platforms

### Railway
1. Go to railway.app
2. "Deploy from GitHub"
3. Select repository
4. Add environment variables
5. Deploy

### PythonAnywhere
1. Upload files or connect GitHub
2. Create Flask app in Web tab
3. Set WSGI file to point to app.py
4. Add environment variables
5. Reload web app

## Troubleshooting

### Common Issues:
1. **Environment Variables Missing:** Double-check all API keys are set
2. **Build Fails:** Ensure requirements.txt is complete
3. **App Won't Start:** Check gunicorn configuration
4. **Excel Download Fails:** Verify Supabase credentials

### Logs:
- Check Render logs in dashboard
- Look for specific error messages
- Ensure all dependencies install correctly

## Support
If deployment fails, check:
1. All environment variables are set correctly
2. API keys are valid and have proper permissions
3. Supabase project is active and accessible
4. GitHub repository is public or properly connected