import responses

from is_api import entities
from tests import sample, utils


def test_rest_client_can_be_initialized(stub_params, is_stub):
    assert is_stub.course == stub_params['course_code']
    assert is_stub.domain == stub_params['domain']
    assert is_stub.faculty == stub_params['faculty_id']
    assert is_stub.url == f"https://{stub_params['domain']}/export/pb_blok_api"


@responses.activate
def test_course_info(stub_params, is_stub):
    url = utils.gen_url(stub_params, ";operace=predmet-info;")
    responses.add(responses.GET, url, body=sample.PREDMET_INFO, status=200, match_querystring=True)
    response: entities.CourseInfo = is_stub.course_info()
    assert response
    assert isinstance(response, entities.CourseInfo)
    assert response.faculty.id == 101
    assert response.faculty.shortcut == 'fi'
    assert response.course.name == "Programování v jazyce C++"
    assert response.course.name_eng == "C++ Programming"
    assert response.course.code == 'PB161'
    assert response.course.number_of_registered_students == 180
    assert response.course.number_of_students == 174
    assert response.course.id == 869944
    assert len(response.seminars) == 1
    seminars = response.seminars
    seminar = seminars[0]
    assert seminar.id == 365290
    assert seminar.label == '01'
    assert seminar.students.count == 15
    assert seminar.students.max == 15
    assert seminar.note is None
    assert seminar.dates.signin_from == "20150901180000"
    assert seminar.dates.signin_to == "20151004000000"
