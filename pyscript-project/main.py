from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('components/menu.html')

@app.route('/draw')
def draw():
    return render_template('draw.html')

@app.route('/chuliu')
def chuliu():
    return render_template('chuliu.html')

@app.route('/teste')
def teste():
    return render_template('teste.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8001)