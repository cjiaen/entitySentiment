from flask import Flask
from flask import request
from flask import render_template, url_for
app = Flask(__name__)

@app.route('/')
def load_main():
    return render_template('main.html')

if __name__ == "__main__":
    #print(app.root_path)
    #print(app.instance_path)
    app.run()