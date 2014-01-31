from flask import Flask, request, Response
from icalendar import Calendar, Event
import urllib2


app = Flask(__name__)
cal_url = 'https://www.imperial.ac.uk/facilitiesmanagement/timetabling/mytimetable/ical/DR1UXPVJ142401/schedule.ics'


@app.route('/timetable.ics', methods=['GET'])
def create():
    unfiltered = get_unfiltered_calendar()
    courses_to_omit = retrieve_courses_to_omit()
    if courses_to_omit:
        calendar = make_filtered_calendar(unfiltered, courses_to_omit)
    else:
        calendar = unfiltered
    return Response(calendar.to_ical(),
                    mimetype="text/calendar",
                    headers={"Content-Disposition":
                             "attachment;filename=timetable.ics"})


def retrieve_courses_to_omit():
    omit = request.args.get('omit')
    if not omit:
        return []
    return omit.split('|')


def make_filtered_calendar(unfiltered_cal, courses_to_omit):
    cal = make_calendar()
    for component in unfiltered_cal.walk():
        if isinstance(component, Event):
            if not filtered(component.get('summary'), courses_to_omit):
                cal.add_component(component)
    return cal


def get_unfiltered_calendar():
    response = urllib2.urlopen(cal_url)
    cal_stream = response.read()
    calendar = Calendar.from_ical(cal_stream)
    response.close()
    return calendar


def make_calendar():
    cal = Calendar()
    cal.add('prodid',
            '-//Ben Chin//Filtered Imperial College CS 2nd Year Timetable//EN')
    cal.add('version', '2.0')
    return cal


def filtered(course_name, courses_to_omit):
    for course in courses_to_omit:
        if course_name.startswith(course):
            return True
    return False

if __name__ == '__main__':
    app.run()
