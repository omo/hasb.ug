
import flask as f

app = f.Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/<int:bugid>')
def redirect(bugid):
    url = "http://trac.webkit.org/changeset/%d" % (bugid)
    return f.redirect(url)

if __name__ == '__main__':
    app.run(DEBUG=True)
