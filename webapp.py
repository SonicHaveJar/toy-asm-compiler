from flask import Flask, request, render_template, flash, send_file
from compiler import Compiler
import random
import io

app = Flask(__name__)

app.secret_key = "i dont like secrets"

XKCDs = ["https://xkcd.com/272/", "https://xkcd.com/557/", "https://xkcd.com/378/", "https://xkcd.com/208/", "https://xkcd.com/1319/"]

@app.route('/', methods=["GET", "POST"])
def index():
    ctx = {}
    if request.method == "POST":
        compiler = Compiler()
        code = request.form.get("code")
        download = request.form.get("download")
        if request.files.get("file").filename:
            file_ = request.files.get("file")
            compiler.lines = [x.decode("utf-8") for x in file_.readlines()]
        elif code:
            compiler = Compiler(code)
        else:
            flash("No se ha subido nada.")
            return render_template("index.html")
        
        ctx = {"bin": compiler()}
        if download:
            mem = io.BytesIO()
            mem.write(ctx["bin"].encode("utf-8"))
            mem.seek(0)
            return send_file(mem, attachment_filename="output.bin", as_attachment=True)

    return render_template("index.html", **ctx)

if __name__ == "__main__":
    app.run(debug=True)