# IS MUNI API python wrapper

Python wrapper for the IS MUNI API.
The IS MUNI Notes API documentation can be found [here](https://is.muni.cz/napoveda/technicka/bloky_api?lang=en).

The output format

## Getting Started

Build status [![CircleCI](https://circleci.com/gh/pestanko/py-is-muni-api.svg?style=svg)](https://circleci.com/gh/pestanko/py-is-muni-api)

### Prerequisites

- requires Python 3.6 or higher

### Install

- Using [PIP](https://pypi.org/project/muni-is-api/):

```bash
pip install muni-is-api
```

- Using the [Poetry](https://python-poetry.org/):


```bash
poetry add https://github.com/pestanko/py-is-muni-api.git
```

## Example

Example usage of the IS API client

```python
import muni_is_api

client = muni_is_api.IsApiClient(
        domain='is.muni.cz',
        token='secret_token',
        faculty_id=1000,
        course_code='PB000'
    )

# Get na course info
course_info = client.course_info()

# Get list of students in the course
students = client.course_list_students(registered=False, terminated=False, inactive=False)

# Get list of stundets in the provided seminary
sem_stud = client.seminar_list_students(seminars=['01', '02'], terminated=False, inactive=False)

# Get list of teachers for the provided seminary
sem_teach = client.seminar_list_teachers(seminars=['01', '02'])

# Get list of all notepads for the course
notepads = client.notepad_list()

# Get notepad content for the specified notepad shortcut and ucos
notepad_content = client.notepad_content(shortcut='hw01', ucos=[1000, 1234, 12345])

# Create a new notepad
client.notepad_new(name="Homework 01", shortcut="hw01", visible=True, complete=False, statistics=True)

# Update a notepad
client.notepad_update(shortcut="hw01", uco=1000, content="Great work! *2", override=True)

# List all exams
exams = client.exams_list(terminated=False, inactive=False)
```



