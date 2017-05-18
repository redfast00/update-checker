from flask import render_template, flash, redirect, url_for, request, abort
from app import app, forms, utils, db, models
from flask_login import current_user, login_required
from werkzeug.contrib.atom import AtomFeed
from pprint import pprint
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
    if form_add.submit.data and form_add.validate_on_submit():
        if form_add.app is None:
            form_add.app = models.AndroidApp(form_add.domain.data)
        form_add.app.subscribers.append(current_user)
        db.session.add(form_add.app)
        db.session.commit()
    if form_remove.to_remove.data and form_remove.validate_on_submit():
        form_remove.app.subscribers.remove(current_user)
        print(form_remove.to_remove.data)
    else:
        utils.flash_errors(form_add)
        utils.flash_errors(form_remove)
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