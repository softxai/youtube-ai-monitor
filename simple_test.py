#!/usr/bin/env python3
"""
Ultra-simple Flask test to debug connection issues
"""

print("🧪 Testing basic Flask functionality...")

try:
    from flask import Flask
    
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return '''
        <h1>🎉 Flask is Working!</h1>
        <p>If you see this, the connection problem is solved.</p>
        <p>Time to run the full dashboard!</p>
        '''
    
    print("✅ Flask imported successfully")
    print("🚀 Starting test server on http://127.0.0.1:5002")
    print("   Press Ctrl+C to stop")
    
    app.run(host='127.0.0.1', port=5002, debug=False)
    
except ImportError as e:
    print(f"❌ Flask not installed: {e}")
    print("💡 Install with: pip3 install flask")
    
except Exception as e:
    print(f"❌ Error starting Flask: {e}")
    print("💡 Try using a different port")
