from flask import render_template, flash, redirect, url_for, request, abort, jsonify
from app import app, forms, utils, db, models
from flask_login import current_user, login_required
from werkzeug.contrib.atom import AtomFeed
from pprint import pprint

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           title = 'Home',
                           user = "none",
                           result = 0,
                           posts = [])

@app.route('/manager', methods=['GET', 'POST'])
@login_required
def manager():
    apps = current_user.subscribed_on
    form_add = forms.AddDomainForm()
    form_remove = forms.RemoveDomainForm()
    feed_address = url_for("recent_feed", feed_uid = current_user.feed_uid, _external=True)
    if request.method == 'POST':
        if form_add.validate_on_submit():
            if form_add.app is None:
                form_add.app = models.AndroidApp(form_add.domain.data)
            form_add.app.subscribers.append(current_user)
            db.session.add(form_add.app)
            db.session.commit()
            apps = current_user.subscribed_on
            return jsonify({"status":"succes", "apps": [ app.android_id for app in current_user.subscribed_on]})
        elif form_add.submit.data:
            errors = {getattr(form_add, field).label.text: errors for field, errors in form_add.errors.items()}
            return jsonify(data=errors)
            utils.flash_errors(form_add)
        if form_remove.to_remove.data and form_remove.validate_on_submit():
            form_remove.app.subscribers.remove(current_user)
            db.session.add(form_remove.app)
            db.session.commit()
            return jsonify({"status":"succes", "apps": [ app.android_id for app in current_user.subscribed_on]})
        elif form_remove.to_remove.data:
            errors = {getattr(form_remove, field).label.text: errors for field, errors in form_remove.errors.items()}
            return jsonify(data=errors)
            utils.flash_errors(form_remove)
        raise InvalidUsage('Error', status_code=410)
    else:
        return render_template('manager.html', form_add=form_add, form_remove=form_remove, apps=apps, feed_address=feed_address)

@app.route('/feed/<feed_uid>/updates.atom')
def recent_feed(feed_uid):
    # user authentication can't be used, so feed_uid gets used instead
    current_user = models.User.query.filter_by(feed_uid=feed_uid).first()
    if not current_user:
        abort(400)

    feed = AtomFeed('App Updates',
        feed_url=request.url, url=request.url_root, author="Update Checker")

    all_updates =  [update for updates in [ app.updates for app in current_user.subscribed_on ] for update in updates]
    articles = sorted(all_updates, key=lambda r: r.timestamp, reverse=True)[:app.config["NUM_UPDATES"]]

    for article in articles:
        text = "Update for {}, version {}".format(article.android_id, article.version)
        feed.add("Android App Update", text,
                 content_type='text',
                 updated=article.timestamp,
                 published=article.timestamp,
                 id=article.id)
    return feed.get_response()