import logging
from typing import List, Optional

from lxml import etree

log = logging.getLogger(__name__)


class Resource:
    def __init__(self, content: etree.Element, base_selector=""):
        self._content = content
        self._base_selector = base_selector

    @property
    def root(self) -> etree.Element:
        return self._content

    def __getitem__(self, item) -> etree.Element:
        selector = self._base_selector + item
        log.debug(f"XPATH SELECTOR \"{selector}]\"")
        result = self.root.xpath(selector)
        log.debug(f"XPATH RESULT \"{selector}]\": {result}")
        return result

    def __call__(self, item: str, default=None) -> Optional[str]:
        result = self[item + "/text()"]
        if not result:
            return default
        result = "".join(result)
        return result

    def _collection(self, selector, klass) -> List:
        result = []
        for (index, _) in enumerate(self.root.xpath(selector)):
            selector = f"{selector}[{index + 1}]/"
            cls_instance = self._klass_init(klass=klass, selector=selector)
            result.append(cls_instance)
        return result

    def _klass_init(self, klass, selector=None):
        selector = selector or self._base_selector
        return klass(self.root, base_selector=selector)


class ChangedSub(Resource):
    @property
    def person(self) -> str:
        return self('ZMENIL')

    @property
    def date(self) -> str:
        return self('ZMENENO')


class Seminar(Resource):
    class StudentsSub(Resource):
        @property
        def max(self) -> int:
            return int(self('MAX_STUDENTU'))

        @property
        def count(self) -> int:
            return int(self('POCET_STUDENTU_VE_SKUPINE'))

    class DatesSub(Resource):
        @property
        def signin_from(self) -> str:
            return self('PRIHLASIT_OD')

        @property
        def signin_to(self) -> str:
            return self('PRIHLASIT_DO')

        @property
        def signout_to(self) -> str:
            return self('ODHLASIT_DO')

    @property
    def id(self) -> int:
        return int(self('SEMINAR_ID'))

    @property
    def label(self) -> str:
        return self('OZNACENI')

    @property
    def changed(self) -> 'ChangedSub':
        return self._klass_init(ChangedSub)

    @property
    def dates(self) -> 'Seminar.DatesSub':
        return self._klass_init(Seminar.DatesSub)

    @property
    def students(self) -> 'Seminar.StudentsSub':
        return self._klass_init(Seminar.StudentsSub)

    @property
    def note(self) -> str:
        return self('POZNAMKA')


class AbstractPerson(Resource):
    @property
    def first_name(self) -> str:
        return self('JMENO')

    @property
    def last_name(self) -> str:
        return self('PRIJMENI')

    @property
    def full_name(self) -> str:
        return self('CELE_JMENO')

    @property
    def uco(self) -> int:
        return int(self('UCO'))


class Teacher(AbstractPerson):
    @property
    def role(self) -> str:
        return self('ROLE')


class CourseInfo(Resource):
    def __init__(self, content: etree.Element, base_selector="/PREDMET_INFO/"):
        super().__init__(content, base_selector=base_selector)

    class CourseSub(Resource):
        @property
        def id(self) -> int:
            return int(self('PREDMET_ID'))

        @property
        def name(self) -> str:
            return self('NAZEV_PREDMETU')

        @property
        def name_eng(self) -> str:
            return self('NAZEV_PREDMETU_ANGL')

        @property
        def code(self) -> str:
            return self('KOD_PREDMETU')

        @property
        def number_of_students(self) -> int:
            return int(self('POCET_ZAPSANYCH_STUDENTU'))

        @property
        def number_of_registered_students(self) -> int:
            return int(self('POCET_ZAREG_STUDENTU'))

    class FacultySub(Resource):
        @property
        def id(self) -> int:
            return int(self('FAKULTA_ID'))

        @property
        def shortcut(self) -> str:
            return self('FAKULTA_ZKRATKA_DOM')

    @property
    def course(self) -> 'CourseInfo.CourseSub':
        return self._klass_init(CourseInfo.CourseSub)

    @property
    def faculty(self) -> 'CourseInfo.FacultySub':
        return self._klass_init(CourseInfo.FacultySub)

    @property
    def seminars(self) -> List[Seminar]:
        return self._collection(selector="SEMINARE/SEMINAR", klass=Seminar)

    @property
    def teachers(self) -> List[Teacher]:
        return self._collection(selector="VYUCUJICI_SEZNAM/VYUCUJICI", klass=Teacher)


class NotepadContent(Resource):
    def __init__(self, content: etree.Element, base_selector="/BLOKY_OBSAH/"):
        super().__init__(content, base_selector=base_selector)

    class StudentSub(Resource):
        @property
        def content(self) -> str:
            return self('OBSAH')

        @property
        def uco(self) -> int:
            return int(self('UCO'))

        @property
        def changed(self) -> ChangedSub:
            return self._klass_init(ChangedSub)

    @property
    def students(self) -> list:
        return self._collection(selector="STUDENT", klass=NotepadContent.StudentSub)


class StudentSub(AbstractPerson):
    @property
    def entity(self):
        return self._content('STUDENT')

    @property
    def study_status(self):
        return self('STAV_STUDIA')

    @property
    def registration_status(self):
        return self('STAV_ZAPISU')

    @property
    def course_termination(self):
        return self('UKONCENI')

    @property
    def has_seminary(self) -> bool:
        return self('STUDENT_NEMA_SEMINAR', '0') != '1'


class CourseStudents(Resource):
    @property
    def students(self) -> List[StudentSub]:
        return self._collection('STUDENT', StudentSub)


class SeminarStudents(Resource):
    @property
    def students(self):
        return self._collection('STUDENT', StudentSub)


class NoteInfo(Resource):
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
        return self._klass_init(ChangedSub)


class NotesInfo(Resource):
    @property
    def notes(self):
        return self._collection('BLOKY_INFO', NoteInfo)


class Exams(Resource):
    @property
    def series(self):
        return None
