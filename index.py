from flask import render_template, redirect, url_for, session
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    return render_template('index.html')