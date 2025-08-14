"""
Flask-based alternative to Streamlit for when Windows socket permissions are too restrictive.
This provides a simpler web interface for the aerospace calculators.
"""

import sys
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if required packages are available"""
    missing = []
    
    try:
        import flask
    except ImportError:
        missing.append("flask")
    
    try:
        import calculators
    except ImportError:
        missing.append("calculators module")
        
    return missing

def install_flask():
    """Install Flask if missing"""
    print("🔧 Installing Flask...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
        print("✅ Flask installed successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to install Flask: {e}")
        return False

def create_simple_app():
    """Create a simple Flask app with calculator functionality"""
    from flask import Flask, render_template_string, request, jsonify
    from calculators import standard_atmosphere, alveolar_PO2
    
    app = Flask(__name__)
    
    # Simple HTML template
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Aerospace Calculators</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2563eb; text-align: center; margin-bottom: 30px; }
            .calculator { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #2563eb; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #1d4ed8; }
            .result { margin-top: 15px; padding: 10px; background: #f0f9ff; border-radius: 4px; }
            .error { background: #fef2f2; color: #dc2626; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Aerospace Calculators</h1>
            <p style="text-align: center; color: #666;">Simplified web interface (Flask-based)</p>
            
            <div class="calculator">
                <h3>Standard Atmosphere Properties</h3>
                <form id="atmosphere-form">
                    <div class="form-group">
                        <label for="altitude">Altitude (ft):</label>
                        <input type="number" id="altitude" min="0" max="60000" value="0" step="1000">
                    </div>
                    <button type="submit">Calculate</button>
                </form>
                <div id="atmosphere-result" class="result" style="display:none;"></div>
            </div>
            
            <div class="calculator">
                <h3>Alveolar Oxygen Pressure</h3>
                <form id="alveolar-form">
                    <div class="form-group">
                        <label for="alt2">Altitude (ft):</label>
                        <input type="number" id="alt2" min="0" max="40000" value="0" step="1000">
                    </div>
                    <div class="form-group">
                        <label for="fio2">FiO₂:</label>
                        <input type="number" id="fio2" min="0" max="1" value="0.21" step="0.01">
                    </div>
                    <button type="submit">Calculate</button>
                </form>
                <div id="alveolar-result" class="result" style="display:none;"></div>
            </div>
        </div>
        
        <script>
        document.getElementById('atmosphere-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const altitude = document.getElementById('altitude').value;
            fetch('/api/atmosphere', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({altitude: parseFloat(altitude)})
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('atmosphere-result');
                if (data.error) {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = 'Error: ' + data.error;
                } else {
                    resultDiv.className = 'result';
                    resultDiv.innerHTML = `
                        <strong>Results for ${altitude} ft:</strong><br>
                        Temperature: ${data.temperature_C.toFixed(2)} °C (${data.temperature_F.toFixed(1)} °F)<br>
                        Pressure: ${data.pressure_hPa.toFixed(2)} hPa<br>
                        Density: ${data.density_kg_m3.toFixed(4)} kg/m³<br>
                        O₂ Partial Pressure: ${data.pO2_hPa.toFixed(2)} hPa
                    `;
                }
                resultDiv.style.display = 'block';
            })
            .catch(error => {
                console.error('Error:', error);
                const resultDiv = document.getElementById('atmosphere-result');
                resultDiv.className = 'result error';
                resultDiv.innerHTML = 'Network error occurred';
                resultDiv.style.display = 'block';
            });
        });
        
        document.getElementById('alveolar-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const altitude = document.getElementById('alt2').value;
            const fio2 = document.getElementById('fio2').value;
            fetch('/api/alveolar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({altitude: parseFloat(altitude), fio2: parseFloat(fio2)})
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('alveolar-result');
                if (data.error) {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = 'Error: ' + data.error;
                } else {
                    resultDiv.className = 'result';
                    resultDiv.innerHTML = `
                        <strong>Results:</strong><br>
                        PAO₂: ${data.pao2.toFixed(1)} mmHg
                    `;
                }
                resultDiv.style.display = 'block';
            })
            .catch(error => {
                console.error('Error:', error);
                const resultDiv = document.getElementById('alveolar-result');
                resultDiv.className = 'result error';
                resultDiv.innerHTML = 'Network error occurred';
                resultDiv.style.display = 'block';
            });
        });
        </script>
    </body>
    </html>
    """
    
    @app.route('/')
    def home():
        return render_template_string(template)
    
    @app.route('/api/atmosphere', methods=['POST'])
    def api_atmosphere():
        try:
            data = request.get_json()
            alt_ft = data['altitude']
            alt_m = alt_ft * 0.3048
            
            result = standard_atmosphere(alt_m)
            return jsonify({
                'temperature_C': result['temperature_C'],
                'temperature_F': result['temperature_C'] * 9/5 + 32,
                'pressure_hPa': result['pressure_Pa'] / 100,
                'density_kg_m3': result['density_kg_m3'],
                'pO2_hPa': result['pO2_Pa'] / 100
            })
        except Exception as e:
            return jsonify({'error': str(e)})
    
    @app.route('/api/alveolar', methods=['POST'])
    def api_alveolar():
        try:
            data = request.get_json()
            alt_ft = data['altitude']
            alt_m = alt_ft * 0.3048
            fio2 = data['fio2']
            
            pao2 = alveolar_PO2(alt_m, fio2, 40.0, 0.8)  # Default PaCO2=40, RQ=0.8
            return jsonify({'pao2': pao2})
        except Exception as e:
            return jsonify({'error': str(e)})
    
    return app

def main():
    """Main function to run the Flask alternative"""
    print("🚀 Starting Flask Alternative for Aerospace Calculators...")
    print("💡 This is a fallback when Streamlit has socket permission issues")
    print("")
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        if 'flask' in missing:
            if not install_flask():
                print("❌ Cannot proceed without Flask")
                return False
        if 'calculators module' in missing:
            print("❌ Cannot find calculators module - make sure you're in the right directory")
            return False
        print("")
    
    try:
        # Create and run the app
        app = create_simple_app()
        
        print("✅ Flask app created successfully")
        print("🌐 Starting server on http://localhost:5000")
        print("📋 The browser will open automatically")
        print("⏹️ Press Ctrl+C to stop the server")
        print("")
        
        # Open browser after a short delay
        import threading
        def open_browser():
            time.sleep(1.5)
            webbrowser.open('http://localhost:5000')
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Run the Flask app
        app.run(host='127.0.0.1', port=5000, debug=False)
        
    except Exception as e:
        print(f"❌ Flask app failed to start: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
