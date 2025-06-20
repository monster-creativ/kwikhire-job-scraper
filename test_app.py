from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('test.html')

@app.route('/test', methods=['POST'])
def test():
    data = request.get_json()
    return jsonify({
        'status': 'success',
        'message': 'Test endpoint working',
        'received_data': data
    })

if __name__ == '__main__':
    app.run(debug=True) 