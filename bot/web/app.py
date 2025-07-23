from flask import Flask, session, request, render_template, redirect, url_for

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/")
def catch():
    if 'username' in session and 'password' in session:
        return 'Logged in'
    return render_template('index.html')  # Отображение шаблона для неавторизованных

@app.route("/login", methods=["GET", "POST"])
def login_user():
    if request.method == "POST":
        session["username"] = request.form["username"]
        session["password"] = request.form["password"]
        return redirect(url_for('catch'))
    return render_template('login.html')  # Форма входа для GET-запроса

@app.route('/logout')  
def logout():
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('catch'))

#url_for указывается endpoint(названия функции), 
#найдя функцию возвращается url по которосу к ней можно обратиться
# также  end_point можно указать