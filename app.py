from flask import Flask, render_template, request, jsonify, make_response
import os
import logging
import json

# Configure logging
logging.basicConfig(
    filename='scraper.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Get the absolute path to the templates directory
TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
logging.info(f"Template directory: {TEMPLATE_DIR}")

app = Flask(__name__, 
           template_folder=TEMPLATE_DIR,
           static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), 'static')))

def json_response(data, status=200):
    response = make_response(jsonify(data), status)
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/')
def index():
    logging.info("Accessing root route")
    try:
        return render_template('index.html')
    except Exception as e:
        logging.error(f"Error rendering template: {str(e)}")
        return str(e), 500

@app.route('/test')
def test():
    logging.info("Accessing test route")
    return json_response({"message": "Test route working"})

@app.route('/scrape', methods=['POST'])
def scrape():
    logging.info("Accessing scrape route")
    try:
        if not request.is_json:
            return json_response({"error": "Request must be JSON"}, 400)

        data = request.get_json()
        logging.info(f"Received data: {data}")

        # For testing, just return the received data
        return json_response({
            "success": True,
            "message": "Test response",
            "received_data": data
        })

    except Exception as e:
        logging.error(f"Error in scrape route: {str(e)}")
        return json_response({"error": str(e)}, 500)

if __name__ == '__main__':
    logging.info("Starting Flask application")
    print(f"Template directory: {TEMPLATE_DIR}")
    print(f"Static directory: {app.static_folder}")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, port=5000) 