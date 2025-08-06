#!/bin/bash
echo "🚀 Setting up ContentStrategist on Replit..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create data directories if they don't exist
mkdir -p data/output

echo "✅ Setup complete!"
echo "🌐 You can now run the app with: python main.py"
echo "🔑 Don't forget to set your API keys in Secrets:"
echo "   - OPENAI_API_KEY (Required)"
echo "   - SERPER_API_KEY (Optional - for trend analysis)"
echo "   - SUPABASE_URL (Optional - for caching)"
echo "   - SUPABASE_KEY (Optional - for caching)"