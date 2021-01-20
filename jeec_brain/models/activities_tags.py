from jeec_brain.database import db
from jeec_brain.models.model_mixin import ModelMixin
from sqlalchemy import Column, Integer, ForeignKey


class ActivitiesTags(db.Model, ModelMixin):
    __tablename__ = 'activities_tags'

    tag_id = Column(Integer, ForeignKey('tags.id'), index=True)
    activity_id = Column(Integer, ForeignKey('activities.id'), index=True)