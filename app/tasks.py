from app import app, db, scheduler, models, scraper
import datetime


@scheduler.scheduled_job("interval", seconds=app.config["UPDATE_INTERVAL"])
def interval_update():
    update_database()

def update_database():
    apps = models.AndroidApp.query.all()
    for app in apps:
        update_app(app)


def update_app(app):
    android_id = app.android_id
    app_info = scraper.get_information(android_id)
    # Check if our information is newer than the information in the database
    for android_update in app.updates:
        if android_update.version == app_info["version"]:
            # This version is already in the database
            return
    # We don't have this version yet, adding it in the database
    update = models.AndroidAppUpdate(
        version=app_info["version"],
        date_updated=app_info["published"],
        timestamp=datetime.datetime.now(),
        android_app=app
    )
    db.session.add(update)
    db.session.commit()