from flask import Flask, request, render_template, url_for, jsonify
import skin_gen

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.json.get('prompt')
    
    skin_gen.generate_skin(prompt)
    
    img_url = url_for('static', filename='output/skin.png')
    return jsonify({"success": True, "img_url": img_url})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)