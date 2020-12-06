from jeec_brain.models.students import Students
from jeec_brain.models.student_activities import StudentActivities
from jeec_brain.models.student_companies import StudentCompanies

class StudentsFinder():

    @classmethod
    def get_from_ist_id(cls, ist_id):
        return Students.query.filter_by(ist_id=ist_id).first()

    @classmethod
    def get_from_external_id(cls, external_id):
        return Students.query.filter_by(external_id=external_id).first()

    @classmethod
    def get_from_id(cls, id):
        return Students.query.filter_by(id=id).first()

    @classmethod
    def get_from_username(cls, username):
        return Students.query.filter_by(username=username).first()

    @classmethod
    def get_from_user_id(cls, user_id):
        return Students.query.filter_by(user_id=user_id).first()
    
    @classmethod
    def get_all(cls):
        return Students.all()

    @classmethod
    def get_top_10(cls):
        return Students.query.order_by(Students.total_points.desc()).limit(10).all()
    
    @classmethod
    def get_from_search(cls, search):
        search = "%{}%".format(search)
        return Students.query.filter(Students.name.ilike(search) | Students.ist_id.ilike(search)).all()

    @classmethod
    def get_from_search_without_student(cls, search, student_external_id):
        search = "%{}%".format(search)
        return Students.query.filter((Students.name.ilike(search) | Students.ist_id.ilike(search)) & (Students.external_id != student_external_id)).all()

    @classmethod
    def get_student_activity_from_id_and_activity_id(cls, student_id, activity_id):
        return StudentActivities.query.filter_by(student_id=student_id, activity_id=activity_id).first()

    @classmethod
    def get_student_company(cls, student, company):
        return StudentCompanies.query.filter_by(student_id=student.id, company_id=company.id).first()