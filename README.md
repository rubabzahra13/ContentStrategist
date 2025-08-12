# 🚀 Content Strategist

A web application that generates strategic Instagram Reels content calendars for entrepreneurs scaling with business strategy.

![Python](https://img.shields.io/badge/Python-3.11+-green) ![Flask](https://img.shields.io/badge/Flask-Web%20App-red)

## ✨ Features

- 🤖 **Intelligent Content Generation** - Advanced content strategy and viral marketing expertise
- 📅 **30-Day Strategic Calendars** - Complete monthly content plans with timing and optimization
- 🔤 **Smart Input Processing** - Handles spelling errors like "ajguzt" → "August" automatically
- 📊 **Professional Excel Export** - Beautifully formatted calendars with 10 strategic columns
- 🕒 **Time-Aware Trends** - Different strategies for past, present, and future months
- 💾 **Intelligent Caching** - Time-based expiration with instant access to previous calendars
- 📱 **Mobile-Responsive** - Works perfectly on phones, tablets, and desktops
- ⚡ **Real-Time Progress** - Live updates during generation process

## 🎯 What You Get

Each generated calendar includes:

- **Strategic Hooks** - Scroll-stopping openers with psychological triggers
- **Timing Breakdowns** - Precise 0-2s, 3-20s, 20-30s content structure
- **Production Notes** - Visual requirements, audio strategies, optimization tips
- **Lead Magnets** - DM collection strategies and conversion optimization
- **Hashtag Strategy** - Mix of trending and niche hashtags for maximum reach
- **Format Variety** - Face-to-cam, screen demos, voiceovers, carousels

## 🚀 Quick Start

### Web Application (Recommended)

1. **Deploy on Replit:**
   - Fork this repository
   - Upload to [Replit.com](https://replit.com)
   - Add environment variables (see below)
   - Run `python app.py`

2. **Set Environment Variables:**
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   SERPER_API_KEY=your_serper_api_key_here  # Optional
   SUPABASE_URL=your_supabase_url_here      # Optional
   SUPABASE_SERVICE_ROLE_KEY=your_key_here  # Optional
   SUPABASE_BUCKET=your_bucket_name_here    # Optional
   SECRET_KEY=your_flask_secret_key_here
   ```

3. **Access your live web app** at the provided Replit URL!

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rubabzahra13/content-strategist.git
   cd content-strategist
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements_web.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open your browser:** http://localhost:5000

### Command Line Interface

```bash
# Install dependencies
pip install -r requirements.txt

# Run the CLI version
python main_cli.py
```

## 📋 Requirements

### Required:
- **OpenAI API Key** - For content generation
- **Python 3.11+** - Runtime environment

### Optional (with fallbacks):
- **Serper API Key** - For trend analysis (fallback trends available)
- **Supabase** - For caching (local storage fallback available)

## 🔧 Project Structure

```
content-strategist/
├── app.py                 # Flask web application
├── main_cli.py           # Original CLI version
├── core/
│   ├── calendar_generator.py   # Content generation engine
│   ├── trend_retriever.py      # Trend analysis
│   ├── excel_exporter.py       # Professional Excel formatting
│   └── cache_handler.py        # Supabase integration
├── utils/
│   ├── helpers.py              # Month normalization
│   └── config.py               # Configuration management
├── templates/              # HTML templates
├── tests/                  # Comprehensive test suite
└── data/output/           # Generated Excel files
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python run_all_tests.py

# Run specific test modules
python -m pytest tests/test_normalize_month.py -v
python -m pytest tests/test_excel_generation.py -v
python -m pytest tests/test_caching_integration.py -v
```

## 🎨 Example Output

The system generates strategic content like this:

**Hook (0-2s):** "If you don't master these 3 skills, you'll be left behind in 12 months"

**Body (3-20s):** "Skill 1: Emotional Intelligence – The foundation of authentic connections. Skill 2: Problem Framing – Ask better questions to get better solutions. Skill 3: Strategic Communication – Your message determines your impact."

**Close (20-30s):** "Which one are you working on right now? Drop it below 👇"

## 🌟 Advanced Features

### Time-Aware Content
- **Past Months:** Historical insights and case studies
- **Current Month:** Real-time trends and current strategies  
- **Future Months:** Predictive content and upcoming trends

### Smart Input Handling
- Automatic spelling correction
- Fuzzy matching for month names
- Multi-word input processing
- Graceful error handling

### Professional Export
- 10-column strategic format
- Beautiful Excel formatting
- Production-ready specifications
- Mobile-optimized layouts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for API services
- Supabase for database and storage
- Flask community for the web framework
- Bootstrap for the beautiful UI components

## 📞 Support

If you have any questions or need help:

1. Check the [Issues](https://github.com/rubabzahra13/content-strategist/issues) page
2. Create a new issue with detailed information
3. Join our community discussions

---

**Built with ❤️ for Content Creators • Professional Grade • Ready for Production**