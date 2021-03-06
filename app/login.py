from app import login_manager, models, app, forms, utils, db
from flask import render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        login_user(form.user, remember=form.remember_me.data)
        return redirect(url_for("manager"))
    else:
        utils.flash_errors(form)
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        user = models.User()
        user.nickname = form.username.data
        user.email = form.email.data
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("manager"))
    else:
        utils.flash_errors(form)
    return render_template('registration.html', form=form)