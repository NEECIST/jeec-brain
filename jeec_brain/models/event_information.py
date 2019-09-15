from jeec_brain.database import db
from jeec_brain.models.model_mixin import ModelMixin
from sqlalchemy.orm import relationship


class EventInformation(ModelMixin, db.Model):
    __tablename__ = 'event_information'
    
    name = db.Column(db.String(100), unique=True, nullable=False)

    date = db.Column(db.String(100))
    email = db.Column(db.String(100))
    address = db.Column(db.String(100))

    facebook_link = db.Column(db.String(100))
    youtube_link = db.Column(db.String(100))
    instagram_link = db.Column(db.String(100))


    def __repr__(self):
        return 'Name: {} | Team: {}'.format(self.name, self.date)