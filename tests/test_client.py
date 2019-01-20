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
