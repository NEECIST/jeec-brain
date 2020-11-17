from jeec_brain.database import db
from jeec_brain.models.model_mixin import ModelMixin
from sqlalchemy.orm import relationship


class ActivityCodes(ModelMixin, db.Model):
    __tablename__ = 'activity_codes'
    
    code = db.Column(db.String(16), unique=True, nullable=False)

    activity = relationship('Activities')
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))

    def __repr__(self):
        return 'Code: {}'.format(self.code)
