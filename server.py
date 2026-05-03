from flask import Flask, request, jsonify, render_template, send_from_directory
import asyncio
from engine import AdvancedDomainEngine

# Initialize the Flask app
app = Flask(__name__)

# Initialize the AdvancedDomainEngine
engine = AdvancedDomainEngine()

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/icon.png')
def favicon():
    return send_from_directory(app.root_path, 'icon.png')


@app.route('/domains', methods=['GET'])
def get_available_domains():
    description = request.args.get('description')
    extension = request.args.get('extension', 'com') # Default to 'com' if not provided

    if not description:
        return jsonify({"error": "'description' parameter is required"}), 400

    try:
        # Run the async engine function
        available_domains = asyncio.run(engine.run_engine(description, extension))
        return jsonify({"description": description, "extension": extension, "available_domains": available_domains})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# To run the Flask app
# In Colab, you might need to expose the port using ngrok or a similar service
# For local testing within Colab, you can run:
#app.run(host='0.0.0.0', port=5000)

# To make it work reliably in Colab for external access, you typically need ngrok
# Example using ngrok (install it first: !pip install pyngrok):
# from pyngrok import ngrok

# # Terminate open tunnels if any
# ngrok.kill()

# # Set up a tunnel to the Flask app's port
# ngrok_tunnel = ngrok.connect(5000)
# print(f" * ngrok tunnel: {ngrok_tunnel.public_url}")
# app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    app.run(debug=True)