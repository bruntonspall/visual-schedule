#!/usr/bin/env python
#
import google.appengine.api.users
from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.ext.webapp import blobstore_handlers


import logging
import jinja2
import webapp2
import json
import os

jinj = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))


class UserDetails(db.Model):
    user = db.UserProperty()


class Picture(db.Model):
    owner = db.ReferenceProperty(UserDetails)
    title = db.StringProperty()
    caption = db.StringProperty()
    full_size_image = db.LinkProperty()


class Schedule(db.Model):
    owner = db.ReferenceProperty(UserDetails)
    last_modified = db.DateTimeProperty(auto_now=True)


class PicturePlacement(db.Model):
    picture = db.ReferenceProperty(Picture)
    schedule = db.ReferenceProperty(Schedule, collection_name='pictures')
    position = db.ListProperty(int)


class PictureAdminHandler(blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/picture')
        template = jinj.get_template('pictureadmin.html')
        self.response.out.write(template.render(
            {
            'uploadurl': upload_url
            }
            ))

    def post(self):
        current_user = google.appengine.api.users.get_current_user()
        if not current_user:
            self.redirect('/signup')
        user = get_user_details(current_user)

        uploaded_files = self.get_uploads()
        blob_info = uploaded_files[0]
        pic = Picture(title="title", caption="caption")
        pic.owner = user
        pic.full_size_image = images.get_serving_url(blob_key=blob_info)
        pic.put()
        self.redirect('/')


def get_picture_placement(picture, schedule):
    pic = Picture.get(picture)
    placement = PicturePlacement.all().filter('picture =', pic).get() or PicturePlacement(schedule=schedule, picture=pic)
    return placement


class ScheduleApiHandler(webapp2.RequestHandler):
    def get(self, schedule):
        schedule = Schedule.get(schedule)
        doc = {}
        doc['id'] = str(schedule.key())
        doc['lastmodified'] = schedule.last_modified.isoformat()
        doc['pictures'] = [
        {'id': str(p.picture.key()),
        'url': p.picture.full_size_image,
        'left': p.position[0],
        'top': p.position[1]}
        for p in schedule.pictures]
        self.response.out.write(json.dumps(doc))

    def post(self, schedule):
        logging.info(self.request.params)
        left, top = self.request.get('left'), self.request.get('top')
        schedule = Schedule.get(schedule)
        placement = get_picture_placement(self.request.get('key'), schedule)
        placement.position = [int(i) for i in [left, top]]
        db.put([placement, schedule])


def get_user_details(user):
    return UserDetails.all().filter('user =', user).get()


def get_schedule(user):
    schedule = Schedule.all().filter('owner =', user).get()
    if not schedule:
        schedule = Schedule(owner=user)
        schedule.put()
    return schedule


class MainHandler(webapp2.RequestHandler):
    def get(self):
        logging.info(self.request.host)
        current_user = google.appengine.api.users.get_current_user()
        if not current_user:
            self.redirect('/signup')
        user = get_user_details(current_user)
        if not user:
            user = UserDetails(user=current_user)
            user.put()
            logging.info("Setting up default library")
            pictures = [
                Picture(owner=user, title="Kitten jumping", caption="Kitten jumping", full_size_image='http://' + self.request.host + '/static/img/kitten1.jpg'),
                Picture(owner=user, title="Kitten running", caption="Kitten running", full_size_image='http://' + self.request.host + '/static/img/kitten2.jpg'),
                Picture(owner=user, title="Ginger kitten", caption="Ginger kitten", full_size_image='http://' + self.request.host + '/static/img/kitten3.jpg')
            ]
            db.put(pictures)

        schedule = get_schedule(user)

        logging.info("Got request for /")
        template = jinj.get_template('index.html')
        self.response.out.write(template.render(
            {
            'user': user,
            'schedule': schedule,
            'library': Picture.all().filter('owner =', user)
            }))


class LogHandler(webapp2.RequestHandler):
    def post(self):
        self.get()

    def get(self):
        logging.info(self.request.get('msg'))


class SignupHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect(google.appengine.api.users.create_login_url())


app = webapp2.WSGIApplication([
        ('/', MainHandler),
        ('/log', LogHandler),
        ('/signup', SignupHandler),
        ('/schedule/(.*)', ScheduleApiHandler),
        ('/picture', PictureAdminHandler),
    ], debug=True)
