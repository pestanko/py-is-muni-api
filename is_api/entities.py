import logging
from typing import List, Optional

from defusedxml.lxml import tostring, RestrictedElement

log = logging.getLogger(__name__)


class Resource:
    def __init__(self, content: RestrictedElement, base_selector=""):
        self._content = content
        self._base_selector = base_selector

    @property
    def root(self) -> RestrictedElement:
        return self._content
    
    @property
    def xml(self) -> str:
        string = tostring(self.root, encoding='utf-8', pretty_print=True)
        return string.decode('utf-8')

    def __getitem__(self, item) -> RestrictedElement:
        selector = self._base_selector + item
        log.trace(f"XPATH SELECTOR \"{selector}]\"")
        result = self.root.xpath(selector)
        log.trace(f"XPATH RESULT \"{selector}]\": {result}")
        return result

    def __call__(self, item: str, default=None) -> Optional[str]:
        result = self[item + "/text()"]
        if not result:
            return default
        result = "".join(result)
        return result

    def _collection(self, selector, klass) -> List:
        result = []
        selector = f"{self._base_selector}{selector}"
        for (index, _) in enumerate(self.root.xpath(selector)):
            selector_inner = f"{selector}[{index + 1}]/"
            cls_instance = self._klass_init(klass=klass, selector=selector_inner)
            result.append(cls_instance)
        return result

    def _klass_init(self, klass, selector=None):
        selector = selector or self._base_selector
        return klass(self.root, base_selector=selector)

    def __str__(self) -> str:
        return self.xml


class ChangedSub(Resource):
    @property
    def person(self) -> int:
        return int(self('ZMENIL'))

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
    def __init__(self, content: RestrictedElement, base_selector="/PREDMET_INFO/"):
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
    def __init__(self, content: RestrictedElement, base_selector="/BLOKY_OBSAH/"):
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
    def __init__(self, content: RestrictedElement, base_selector="/PREDMET_STUDENTI_INFO/"):
        super().__init__(content, base_selector=base_selector)

    @property
    def students(self) -> List[StudentSub]:
        return self._collection('STUDENT', StudentSub)


class SeminarShared(Resource):
    @property
    def name(self) -> str:
        return self('OZNACENI')

    @property
    def id(self) -> int:
        return int(self('SEMINAR_ID'))


class SeminarTeachers(Resource):
    def __init__(self, content: RestrictedElement, base_selector="/SEMINAR_CVICICI_INFO/"):
        super().__init__(content, base_selector=base_selector)

    @property
    def seminars(self) -> List['SeminarTeachers.SeminarSub']:
        return self._collection('SEMINAR', SeminarTeachers.SeminarSub)

    class SeminarSub(SeminarShared):
        @property
        def teachers(self) -> List['StudentSub']:
            return self._collection('CVICICI', Teacher)


class SeminarStudents(Resource):
    def __init__(self, content: RestrictedElement, base_selector="/SEMINAR_STUDENTI_INFO/"):
        super().__init__(content, base_selector=base_selector)

    @property
    def seminars(self) -> List['SeminarStudents.SeminarSub']:
        return self._collection('SEMINAR', SeminarStudents.SeminarSub)

    class SeminarSub(SeminarShared):
        @property
        def students(self) -> List['StudentSub']:
            return self._collection('STUDENT', StudentSub)


class NoteInfo(Resource):
    @property
    def id(self) -> int:
        return int(self('BLOK_ID'))

    @property
    def name(self) -> str:
        return self('JMENO')

    @property
    def show_statistic(self) -> bool:
        return self('STUDENTOVI_ZOBRAZIT_STATISTIKU') == 'a'

    @property
    def type_id(self) -> str:
        return self('TYP_ID')

    @property
    def type_name(self) -> str:
        return self('TYP_NAZEV')

    @property
    def shortcut(self) -> str:
        return self('ZKRATKA')

    @property
    def changed(self) -> ChangedSub:
        return self._klass_init(ChangedSub)


class NotesList(Resource):
    def __init__(self, content: RestrictedElement, base_selector="/POZN_BLOKY_INFO/"):
        super().__init__(content, base_selector=base_selector)

    @property
    def notes(self) -> List[NoteInfo]:
        return self._collection('POZN_BLOK', NoteInfo)


class Exams(Resource):
    @property
    def series(self):
        return None
