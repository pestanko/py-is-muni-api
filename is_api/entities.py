from typing import List


class Resource(object):

    def __init__(self, content):
        self._content = content

    @property
    def entity(self):
        return self._content

    def __getitem__(self, item):
        return self.entity[item]

    def __setitem__(self, key, value):
        self.entity[key] = value


class ChangedSub(Resource):
    @property
    def person(self):
        return self['ZMENIL']

    @property
    def date(self):
        return self['ZMENENO']


class Seminar(Resource):
    class StudentsSub(Resource):
        @property
        def max(self) -> int:
            return int(self['MAX_STUDENTU'])

        @property
        def count(self) -> int:
            return int(self['POCET_STUDENTU_VE_SKUPINE'])

    class DatesSub(Resource):
        @property
        def signin_from(self) -> str:
            return self['PRIHLASIT_OD']

        @property
        def signin_to(self) -> str:
            return self['PRIHLASIT_DO']

        @property
        def signout_to(self) -> str:
            return self['ODHLASIT_DO']

    @property
    def id(self) -> int:
        return int(self['SEMINAR_ID'])

    @property
    def label(self) -> str:
        return self['OZNACENI']

    @property
    def changed(self) -> 'ChangedSub':
        return ChangedSub(self)

    @property
    def dates(self) -> 'Seminar.DatesSub':
        return Seminar.DatesSub(self)

    @property
    def students(self) -> 'Seminar.StudentsSub':
        return Seminar.StudentsSub(self)

    @property
    def entity(self) -> dict:
        return self._content

    @property
    def note(self) -> str:
        return self['POZNAMKA']


class AbstractPerson(Resource):
    @property
    def first_name(self) -> str:
        return self['JMENO']

    @property
    def last_name(self) -> str:
        return self['PRIJIMENI']

    @property
    def full_name(self) -> str:
        return self['CELE_JMENO']

    @property
    def uco(self) -> int:
        return self['UCO']


class Teacher(AbstractPerson):
    @property
    def entity(self) -> dict:
        return self._content

    @property
    def role(self) -> str:
        return self['ROLE']


class CourseInfo(Resource):
    class CourseSub(Resource):
        @property
        def id(self):
            return int(self['PREDMET_ID'])

        @property
        def name(self):
            return self['NAZEV_PREDMETU']

        @property
        def name_eng(self):
            return self['NAZEV_PREDMETU_ANGL']

        @property
        def code(self):
            return self['KOD_PREDMETU']

        @property
        def number_of_students(self):
            return int(self['POCET_ZAPSANYCH_STUDENTU'])

        @property
        def number_of_registered_students(self):
            return int(self['POCET_ZAREG_STUDENTU'])

    class FacultySub(Resource):
        @property
        def id(self):
            return int(self['FAKULTA_ID'])

        @property
        def shortcut(self):
            return self['FAKULTA_ZKRATKA_DOM']

    @property
    def entity(self):
        return self._content['PREDMET_INFO']

    @property
    def course(self):
        return CourseInfo.CourseSub(self)

    @property
    def faculty(self):
        return CourseInfo.FacultySub(self)

    @property
    def seminars(self) -> List[Seminar]:
        return [Seminar(sem) for sem in self['SEMINARE'].values()]

    @property
    def teachers(self) -> List[Teacher]:
        return [Teacher(teach) for teach in self['VYUCUJICI_SEZNAM'].values()]


class NotepadContent(Resource):
    class StudentSub(Resource):
        @property
        def entity(self) -> dict:
            return self._content

        @property
        def content(self) -> str:
            return self['OBSAH']

        @property
        def uco(self) -> int:
            return self['UCO']

        @property
        def changed(self) -> ChangedSub:
            return ChangedSub(self)

    @property
    def entity(self) -> dict:
        return self._content['BLOKY_OBSAH']

    @property
    def students(self) -> list:
        return [NotepadContent.StudentSub(stud) for stud in self.entity.values()]


class StudentSub(AbstractPerson):
    @property
    def entity(self):
        return self._content['STUDENT']

    @property
    def study_status(self):
        return self['STAV_STUDIA']

    @property
    def registration_status(self):
        return self['STAV_ZAPISU']

    @property
    def course_elimination(self):
        return self['UKONCENI']

    @property
    def has_seminary(self) -> bool:
        return self._content.get('STUDENT_NEMA_SEMINAR', '0') != '1'


class CourseStudents(Resource):

    @property
    def entity(self):
        return self._content['PREDMET_STUDENTI_INFO']

    @property
    def students(self):
        return [StudentSub(stud) for stud in self.entity]


class SeminarStudents(Resource):
    @property
    def entity(self):
        return self._content['SEMINAR_STUDENTI_INFO']

    @property
    def students(self):
        return [StudentSub(stud) for stud in self.entity]


class NoteInfo(Resource):
    @property
    def entity(self):
        return self._content['POZN_BLOK']

    @property
    def id(self):
        return self['BLOK_ID']

    @property
    def name(self):
        return self['JMENO']

    @property
    def show_statistic(self):
        return self['STUDENTOVI_ZOBRAZIT_STATISTIKU']

    @property
    def type_id(self):
        return self['TYP_ID']

    @property
    def type_name(self):
        return self['TYP_NAZEV']

    @property
    def shortcut(self):
        return self['ZKRATKA']

    @property
    def changed(self) -> ChangedSub:
        return ChangedSub(self)


class NotesInfo(Resource):
    @property
    def entity(self):
        return self._content['POZN_BLOKY_INFO']

    @property
    def notes(self):
        return [NoteInfo(note) for note in self.entity]


class Exams(Resource):
    @property
    def entity(self):
        return self._content['TERMINY']

    @property
    def series(self):
        return None
