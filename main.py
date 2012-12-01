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
import re

ipadRegex = re.compile(r"iPad|iPhone")

jinj = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))


def login_required(func):
    def do_func(self, *args, **kwargs):
        logging.info(self.request.host)
        current_user = google.appengine.api.users.get_current_user()
        if not current_user:
            self.redirect('/signup')
        self.user = UserDetails.get_current()
        if not self.user:
            self.redirect('/setup')
        return func(self, *args, **kwargs)

    return do_func


class UserDetails(db.Model):
    user = db.UserProperty()

    @staticmethod
    def get_for_user(user):
        return UserDetails.all().filter('user =', user).get()

    @staticmethod
    def get_current():
        return UserDetails.all().filter('user =', google.appengine.api.users.get_current_user()).get()


class Picture(db.Model):
    owner = db.ReferenceProperty(UserDetails)
    title = db.StringProperty()
    caption = db.StringProperty()
    full_size_image = db.LinkProperty()


class Schedule(db.Model):
    owner = db.ReferenceProperty(UserDetails)
    last_modified = db.DateTimeProperty(auto_now=True)

    @staticmethod
    def get_for_user(user):
        schedule = Schedule.all().filter('owner =', user).get()
        if not schedule:
            schedule = Schedule(owner=user)
            schedule.put()
        logging.info(",".join([str(pic) for pic in schedule.pictures]))
        return schedule


class PicturePlacement(db.Model):
    picture = db.ReferenceProperty(Picture)
    schedule = db.ReferenceProperty(Schedule, collection_name='pictures')
    position = db.ListProperty(int)

    @staticmethod
    def get_or_create(key, schedule):
        logging.info("Looking for placement %s" % (key))
        placement = PicturePlacement.get(key)
        return placement


class PictureAdminHandler(blobstore_handlers.BlobstoreUploadHandler):
    @login_required
    def get(self):
        upload_url = blobstore.create_upload_url('/picture')
        template = jinj.get_template('pictureadmin.html')
        self.response.out.write(template.render(
            {
            'uploadurl': upload_url
            }
            ))

    @login_required
    def post(self):
        uploaded_files = self.get_uploads()
        blob_info = uploaded_files[0]
        pic = Picture(title="title", caption="caption")
        pic.owner = self.user
        pic.full_size_image = images.get_serving_url(blob_key=blob_info)
        pic.put()
        self.redirect('/')


class ScheduleApiHandler(webapp2.RequestHandler):
    @login_required
    def get(self, schedulekey):
        schedule = Schedule.get(schedulekey)
        doc = {}
        doc['id'] = str(schedule.key())
        doc['lastmodified'] = schedule.last_modified.isoformat()
        doc['pictures'] = [
        {'id': str(p.key()),
        'picture': str(p.picture.key()),
        'url': p.picture.full_size_image,
        'left': p.position[0],
        'top': p.position[1]}
        for p in schedule.pictures]
        self.response.out.write(json.dumps(doc))

    @login_required
    def post(self, schedulekey):
        logging.info(self.request.params)
        left, top = self.request.get('left'), self.request.get('top')
        key = self.request.get('key')
        schedule = Schedule.get(schedulekey)
        if self.request.get('type') == "placement":
            placement = PicturePlacement.get_or_create(key, schedule)
        else:
            placement = PicturePlacement(schedule=schedule, picture=Picture.get(key))

        placement.position = [int(i) for i in [left, top]]
        db.put([placement, schedule])
        self.response.out.write(json.dumps(str(placement.key())))


class ApiPlacementHandler(webapp2.RequestHandler):
    @login_required
    def get(self, schedulekey, placementkey):
        placement = PicturePlacement.get(placementkey)
        doc = {}
        doc['id'] = str(placement.key())
        doc['picture'] = placement.picture.key()
        self.response.out.write(json.dumps(doc))

    @login_required
    def delete(self, schedulekey, placementkey):
        placement = PicturePlacement.get(placementkey)
        db.delete(placement)

    @login_required
    def post(self, schedule):
        logging.info(self.request.params)
        left, top = self.request.get('left'), self.request.get('top')
        key = self.request.get('key')
        schedule = Schedule.get(schedule)
        if self.request.get('type') == "placement":
            placement = PicturePlacement.get_or_create(key, schedule)
        else:
            placement = PicturePlacement(schedule=schedule, picture=Picture.get(key))

        placement.position = [int(i) for i in [left, top]]
        db.put([placement, schedule])
        self.response.out.write(json.dumps(str(placement.key())))

class UserSetupHandler(webapp2.RequestHandler):
    def get(self):
        current_user = google.appengine.api.users.get_current_user()
        if not current_user:
            self.redirect('/signup')
        user = UserDetails(user=current_user)
        user.put()
        logging.info("Setting up default library")
        pictures = [
            Picture(owner=user, title="Kitten jumping", caption="Kitten jumping", full_size_image='http://' + self.request.host + '/static/img/kitten1.jpg'),
            Picture(owner=user, title="Kitten running", caption="Kitten running", full_size_image='http://' + self.request.host + '/static/img/kitten2.jpg'),
            Picture(owner=user, title="Ginger kitten", caption="Ginger kitten", full_size_image='http://' + self.request.host + '/static/img/kitten3.jpg')
        ]
        db.put(pictures)


class MainHandler(webapp2.RequestHandler):
    @login_required
    def get(self):
        logging.info(self.request.environ)
        if ipadRegex.search(self.request.environ["HTTP_USER_AGENT"]):
            self.redirect("/display")

        schedule = Schedule.get_for_user(self.user)

        logging.info("Got request for /")
        template = jinj.get_template('index.html')
        self.response.out.write(template.render(
            {
            'user': self.user,
            'schedule': schedule,
            'library': Picture.all().filter('owner =', self.user),
            'logout_url': google.appengine.api.users.create_logout_url("/")
            }))


class DisplayHandler(webapp2.RequestHandler):
    @login_required
    def get(self):
        schedule = Schedule.get_for_user(self.user)

        template = jinj.get_template('schedule.html')
        self.response.out.write(template.render(
            {
            'user': self.user,
            'schedule': schedule,
            }))


class LogHandler(webapp2.RequestHandler):
    def post(self):
        self.get()

    def get(self):
        logging.info(self.request.get('msg'))


class SignupHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect(google.appengine.api.users.create_login_url())

from webapp2 import Route

app = webapp2.WSGIApplication([
        ('/', MainHandler),
        ('/display', DisplayHandler),
        ('/log', LogHandler),
        ('/signup', SignupHandler),
        Route('/schedule/<schedulekey>', ScheduleApiHandler),
        Route('/schedule/<schedulekey>/<placementkey>', ApiPlacementHandler),
        ('/picture', PictureAdminHandler),
    ], debug=True)
