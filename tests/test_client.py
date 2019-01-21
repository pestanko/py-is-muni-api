import responses

from is_api import entities
from tests import sample, utils


def _add_url_rule(url, body, status=200):
    responses.add(responses.GET, url, body=body, status=status, match_querystring=True)


def test_rest_client_can_be_initialized(stub_params, is_stub):
    assert is_stub.course == stub_params['course_code']
    assert is_stub.domain == stub_params['domain']
    assert is_stub.faculty == stub_params['faculty_id']
    assert is_stub.url == f"https://{stub_params['domain']}/export/pb_blok_api"


@responses.activate
def test_course_info(stub_params, is_stub):
    url = utils.gen_url(stub_params, ";operace=predmet-info;")
    _add_url_rule(url, body=sample.PREDMET_INFO)
    response: entities.CourseInfo = is_stub.course_info()
    assert response
    assert isinstance(response, entities.CourseInfo)
    assert response.faculty.id == 101
    assert response.faculty.shortcut == 'fi'
    assert response.course.name == "Programování v jazyce C++"
    assert response.course.name_eng == "C++ Programming"
    assert response.course.code == 'PB161'
    assert response.course.number_of_registered_students == 120
    assert response.course.number_of_students == 110
    assert response.course.id == 123456
    assert len(response.seminars) == 1
    seminars = response.seminars
    seminar = seminars[0]
    assert seminar.id == 12364
    assert seminar.label == '01'
    assert seminar.students.count == 15
    assert seminar.students.max == 15
    assert seminar.note is None
    assert seminar.dates.signin_from == "20150901180000"
    assert seminar.dates.signin_to == "20151004000000"


@responses.activate
def test_notes_content(stub_params, is_stub):
    url = utils.gen_url(stub_params, ";operace=blok-dej-obsah;zkratka=foo;")
    responses.add(responses.GET, url, body=sample.BLOCKS_CONTENT,
                  status=200, match_querystring=True)
    _add_url_rule(url, body=sample.BLOCKS_CONTENT)
    response: entities.NotepadContent = is_stub.notepad_content(shortcut='foo')
    assert response
    assert isinstance(response, entities.NotepadContent)
    assert len(response.students) == 2
    student1: entities.NotepadContent.StudentSub = response.students[0]
    assert student1.uco == 444111000
    assert student1.changed.date == "20160111104208"
    assert student1.content == "25 bodů"


@responses.activate
def test_course_list_students(stub_params, is_stub):
    url = utils.gen_url(stub_params, ";operace=predmet-seznam")
    _add_url_rule(url, body=sample.COURSE_LIST_STUDENTS)
    response: entities.CourseStudents = is_stub.course_list_students()

    assert len(response.students) == 2
    student1 = response.students[0]
    assert student1.uco == 444555666
    assert student1.course_termination == 'z'
    assert student1.first_name == 'Jan'
    assert student1.last_name == 'Hruska'
    assert student1.full_name == 'Mgr. Jan Hruska'
    assert student1.study_status == 'aktivní'
    assert student1.registration_status == 'zapsáno'
    assert not student1.has_seminary


@responses.activate
def test_seminary_list_students(stub_params, is_stub):
    url = utils.gen_url(stub_params, ";operace=seminar-seznam;seminar=01;seminar=02")
    _add_url_rule(url, body=sample.SEMINARY_LIST_STUDENTS)
    response: entities.SeminarStudents = is_stub.seminar_list_students(seminars=['01', '02'])

    assert len(response.seminars) == 2
    seminar1 = response.seminars[0]
    assert seminar1.id == 11111111111
    assert seminar1.name == '01'
    assert len(seminar1.students) == 1
    student = seminar1.students[0]
    assert student.uco == 4445557777
    assert student.course_termination == 'z'
    assert student.full_name == 'What ever'
    assert student.first_name == 'What'
    assert student.last_name == 'Ever'


@responses.activate
def test_seminary_list_teachers(stub_params, is_stub):
    url = utils.gen_url(stub_params, ";operace=seminar-cvicici-seznam;seminar=01;seminar=02")
    _add_url_rule(url, body=sample.SEMINARY_LIST_TEACHERS)
    response: entities.SeminarTeachers = is_stub.seminar_list_teachers(seminars=['01', '02'])
    assert len(response.seminars) == 2
    seminar1 = response.seminars[0]
    assert seminar1.id == 123456
    assert seminar1.name == '01'
    assert len(seminar1.teachers) == 1
    teacher = seminar1.teachers[0]
    assert teacher.uco == 4445557777
    assert teacher.full_name == 'RNDr. Mgr. What ever'
    assert teacher.first_name == 'What'
    assert teacher.last_name == 'Ever'


@responses.activate
def test_list_notes(stub_params, is_stub):
    url = utils.gen_url(stub_params, ";operace=bloky-seznam;")
    _add_url_rule(url, body=sample.NOTES_LIST)
    response: entities.NotesList = is_stub.notepad_list()
    assert len(response.notes) == 1
    note = response.notes[0]
    assert note.id == 5545421544412
    assert note.name == 'Test X'
    assert note.show_statistic
    assert note.shortcut == 'tst_x'
    assert note.changed.person == 456698545255
    assert note.changed.date == '20160112115151'
    assert note.type_id == '1'
    assert note.type_name == 'obecný blok'


@responses.activate
def test_new_notepad(stub_params, is_stub):
    url = utils.gen_url(stub_params, ";operace=blok-novy;jmeno=Nový poznámkový blok;zkratka=blok4;"
                                     "statistika=n;nahlizi=n;nedoplnovat=n")
    _add_url_rule(url, body="<BLOK_NOVY>Úspěšně uloženo.</BLOK_NOVY>")
    response: entities.Resource = is_stub.notepad_new(shortcut='blok4',
                                                      name='Nový poznámkový blok',
                                                      statistic=False)

    assert response is not None
    assert response('/BLOK_NOVY') == "Úspěšně uloženo."


@responses.activate
def test_add_content_to_notepad(stub_params, is_stub):
    content = "Foo points *2"
    url = utils.gen_url(stub_params, f";operace=blok-pis-student-obsah;zkratka=blok4;"
                                     f"uco=123456;obsah={content};prepis=a")
    _add_url_rule(url, body="<ZAPIS>Úspěšně uloženo.</ZAPIS>")
    response: entities.Resource = is_stub.notepad_update(shortcut='blok4',
                                                         uco='123456',
                                                         content=content)

    assert response is not None
    assert response('/ZAPIS') == "Úspěšně uloženo."
