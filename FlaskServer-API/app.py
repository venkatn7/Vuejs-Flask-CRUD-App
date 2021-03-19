from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return "Hey There!"

@app.route('/test')
def test():
    return "Hey test passed! :)"



if __name__ == '__main__':
    app.run()
