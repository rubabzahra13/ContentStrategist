# 🚀 Instant Deployment Options

## Option 1: GitHub Codespaces (Recommended - 1 Click!)

### Steps:
1. **Go to your GitHub repository:** https://github.com/rubabzahra13/ContentStrategist
2. **Click the green "Code" button**
3. **Click "Codespaces" tab**
4. **Click "Create codespace on main"**
5. **Wait 2-3 minutes for setup**
6. **In the terminal, run:**
   ```bash
   # Create your .env file with your API keys
   cp env_template.txt .env
   # Edit .env with your actual keys (use the file editor)
   
   # Run the app
   python main.py
   ```
7. **Click the popup to open in browser**
8. **Your app is live!**

**Pros:**
- ✅ Completely free (60 hours/month)
- ✅ Zero setup required
- ✅ Runs in browser
- ✅ Auto-installs dependencies

---

## Option 2: Local Development (If you have Python)

### Steps:
1. **Clone the repository:**
   ```bash
   git clone https://github.com/rubabzahra13/ContentStrategist.git
   cd ContentStrategist
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp env_template.txt .env
   # Edit .env with your API keys
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

5. **Open browser to:** http://localhost:5000

---

## Option 3: Gitpod (Alternative Cloud IDE)

### Steps:
1. **Go to:** https://gitpod.io/#https://github.com/rubabzahra13/ContentStrategist
2. **Wait for workspace to load**
3. **Set up .env file with your API keys**
4. **Run:** `python main.py`
5. **Click the popup to open in browser**

---

## Environment Variables Needed:

Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_BUCKET=your_supabase_storage_bucket_name
SECRET_KEY=your_flask_secret_key
```

## 🎯 **Recommendation:**
**Use GitHub Codespaces** - it's the easiest option and requires literally just clicking a button!