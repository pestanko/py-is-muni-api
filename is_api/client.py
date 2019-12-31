import logging

import requests
from defusedxml.lxml import RestrictedElement

from typing import List, Dict

from is_api import entities, utils

log = logging.getLogger(__name__)

"""
URL: https://is.muni.cz/auth/napoveda/technicka/bloky_api?fakulta=1433;obdobi=7024;predmet=990599
"""


class IsApiClient:
    def __init__(self, domain: str, token: str, course_code: str, faculty_id: int):
        """Creates IS API client
        Args:
            domain(str): Is domain (ex. is.muni.cz)
            token(str): Token for the Notes api
            course_code(str): Course code
            faculty_id(int): Id of the faculty
        """
        self._http = HttpClient(domain, token, course_code, faculty_id)
        log.debug(f"[INIT] Created client {self.http}")

    @property
    def http(self) -> 'HttpClient':
        """Gets instance of the HTTP Client
        Returns(HttpClient): Http client instance
        """
        return self._http

    @property
    def url(self) -> str:
        """Ges an url to the IS NOTES API

        Returns(str): Full api url
        """
        return self.http.api_url

    @property
    def domain(self) -> str:
        """Domain for the client

        Returns(str): Domain
        """
        return self.http.domain

    @property
    def course(self) -> str:
        """Course code name

        Returns(str): Course code name
        """
        return self.http.course

    @property
    def faculty(self) -> int:
        """Faculty ID
        Returns(int): Faculty ID
        """
        return self.http.faculty

    def course_info(self) -> entities.CourseInfo:
        """
        Returns(entities.CourseInfo): Course info

        """
        log.debug(f"[READ] Course info")
        return self._create_resource('predmet-info', {}, cls=entities.CourseInfo)

    def course_list_students(self, registered: bool = False, terminated: bool = False,
                             inactive: bool = False) -> entities.CourseStudents:
        """List all of the students in the course

        Args:
            registered(bool): Also show the registered students
            terminated(bool): Also show the students with theirs studies terminated
            inactive(bool): Also show an inactive students

        Returns(Resource): Gets an instance of the list of students
        """
        params = {}

        if registered:
            params['zareg'] = 'a'

        if terminated:
            params['vcukonc'] = 'a'

        if inactive:
            params['vcneaktiv'] = 'a'
        log.debug(f"[LIST] Get list of students in the course with params: {params}")
        return self._create_resource('predmet-seznam', params,
                                     cls=entities.CourseStudents)

    def seminar_list_students(self, seminars: List[str], terminated: bool = False,
                              inactive: bool = False) -> entities.SeminarStudents:
        """List students in the seminars

        Args:
            seminars(List[str]): List of seminars
            terminated(bool): Also show the students with theirs studies terminated
            inactive(bool): Also show an inactive students

        Returns(Resource): Resource instance
        """
        params = {'seminar': seminars}
        if terminated:
            params['vcukonc'] = 'a'

        if inactive:
            params['vcneaktiv'] = 'a'

        log.debug(f"[LIST] Get list of students in the course's seminaries with params: {params}")
        return self._create_resource('seminar-seznam', params,
                                     cls=entities.SeminarStudents)

    def seminar_list_teachers(self, seminars: List[str]) -> entities.SeminarTeachers:
        """List teachers in the seminars

        Args:
            seminars(list[str]): List of seminars

        Returns(Resource): Resource instance
        """
        params = {'seminar': seminars}
        log.debug(f"[LIST] Get list of teachers in the course's seminaries with params: {params}")
        return self._create_resource('seminar-cvicici-seznam', params,
                                     cls=entities.SeminarTeachers)

    def notepad_content(self, shortcut: str, ucos: List[int] = None) -> entities.NotepadContent:
        """Gets notepad content
        Args:
            shortcut(str): Shortcut name of the notepad
            ucos(List[int]): List of students' ucos

        Returns(Resource): Resource instance
        """
        params = dict(zkratka=shortcut)
        if ucos:
            params['uco'] = ucos
        log.debug(f"[READ] Get notepad content with params: {params}")
        return self._create_resource('blok-dej-obsah', params, cls=entities.NotepadContent)

    def notepad_list(self) -> entities.NotesList:
        """List of all notepads
        Returns(Resource): Gets instance of the resources
        """
        log.debug(f"[LIST] Get notepads list.")
        return self._create_resource('bloky-seznam', {}, cls=entities.NotesList)

    def notepad_new(self, name: str, shortcut: str,
                    visible: bool = False, complete: bool = True,
                    statistic: bool = False) -> entities.Resource:
        """Creates a new notepad
        Args:
            name(str): Name of the notepad
            shortcut(str): shortcut of the notepad
            visible(bool): Should the notepad be visible
            complete(bool): Shoult not be completed
            statistic(bool): Should the statistic be generated

        Returns(entities.Resource):

        """
        params = dict(jmeno=name, zkratka=shortcut)

        params['nahlizi'] = 'a' if visible else 'n'
        params['nedoplnovat'] = 'a' if not complete else 'n'
        params['statistika'] = 'a' if statistic else 'n'

        log.info(f"[NOTES] Create notepad with params: {params} ")
        return self._create_resource('blok-novy', params)

    def notepad_update(self, shortcut: str, uco: int, content: str,
                       last_change: str = None, override: bool = True) -> entities.Resource:
        """Updates notepad content
        Args:
            shortcut(str): Notepad shortcut identification
            uco(str): UCO
            content(str): Content
            last_change(str): Format: YYYYMMDDHH24MISS
            override(bool): Overrides the content

        Returns(etree.Element): Parsed XML response
        """
        params = dict(
            zkratka=shortcut,
            uco=uco,
            obsah=content
        )
        if last_change:
            params['poslzmeneno'] = last_change
        if override:
            params['prepis'] = 'a'

        log.info(f"[NOTES] Update notepad with params: {params} ")
        return self._create_resource('blok-pis-student-obsah', params)

    def exams_list(self, terminated: bool = False, inactive: bool = False):
        """Gets a list of exams
        Args:
            terminated(bool): Also show the students with theirs studies terminated
            inactive(bool): Also show an inactive students
        Returns:
        """
        params = {}
        if terminated:
            params['vcukonc'] = 'a'

        if inactive:
            params['vcneaktiv'] = 'a'
        return self._create_resource('terminy-seznam', params)

    def _create_resource(self, operation: str, params: Dict = None, cls=entities.Resource):
        params = params or {}
        resp = self.http.operation(operation=operation, **params)
        return cls(resp)


class HttpClient:
    __slots__ = ('_session', '__fail', '__faculty_id',
                 '__course', '__token', '__domain')

    def __init__(self, domain: str, token: str, course_code: str,
                 faculty_id: int, fail: bool = True):
        """Creates HTTP Client wrapper
        Args:
            domain(str): Is domain (ex. is.muni.cz)
            token(str): Token for the Notes api
            course_code(str): Course code
            faculty_id(int): Id of the faculty
            fail(bool): Throw an exception if the request has not been successful
        """
        self.__domain = domain
        self.__token = token
        self.__course = course_code
        self.__faculty_id = faculty_id
        self.__fail = fail
        self._session = None

    @property
    def session(self) -> requests.Session:
        if self._session is None:
            self._session = requests.Session()
        return self._session

    @property
    def api_url(self) -> str:
        """Ges an url to the IS NOTES API

        Returns(str): Full url
        """
        return f"https://{self.domain}/export/pb_blok_api"

    @property
    def domain(self) -> str:
        """Domain for the client

        Returns(str): Domain
        """
        return self.__domain

    @property
    def course(self) -> str:
        """Course code name

        Returns(str): Course code name
        """
        return self.__course

    @property
    def faculty(self) -> int:
        """Faculty ID
        Returns(int): Faculty ID
        """
        return self.__faculty_id

    def operation(self, operation, **params) -> RestrictedElement:
        """Invokes operation of the API
        Args:
            operation(str): Name of the operation
            **params: Optional params for the operation

        Returns: Resource instance

        """

        prepared = dict(klic=self.__token, fakulta=self.faculty, kod=self.course)
        response = utils.make_get_request(
            session=self.session,
            url=self.api_url,
            params={**params, **prepared, "operace": operation},
            fail=self.__fail
        )

        resource = utils.serialize(response=response)
        log.debug(f"[SERIAL] Serialized response: {resource}")
        return resource

    def __str__(self):
        return f"[{self.domain}]: (FAC={self.faculty}, COURSE={self.course})"
