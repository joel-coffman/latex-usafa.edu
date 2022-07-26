#!/usr/bin/env python

import argparse
from datetime import date
import math
import os
import shutil
import sys

import jinja2
import numpy
import pandas
import scipy.stats


def create_report(path, template, context):
    """Save a report to the specified path.

    :param path: path for the report
    :param template: Jinja2 template
    :param context: Jinja2 context with variables for a template
    """
    directory = os.path.dirname(path)
    if not os.path.isdir(directory):
        os.makedirs(directory)

    # NOTE: Do not overwrite existing report if unchanged
    #   Overwriting an existing report updates the file's timestamp, which
    # causes `make` to recompile the report. Recompiling the report isn't
    # necessary, though, unless the report has changed. Thus, it would be
    # better to write the file only if it differs from the existing report.
    content = template.render(context)
    write = True

    if os.path.exists(path):
        with open(path, 'r') as fp:
            existing = fp.read()

        write = not (content == existing)

    if write is True:
        with open(path, 'w') as fp:
            fp.write(content)

        shutil.copy('./templates/Makefile',
                    os.path.join(directory, 'Makefile'))


def escape(value):
    '''Replace special characters in LaTeX with "safe" substitution'''
    escaped = value
    for character in ['\\', '&', '#', '_', '$']:
        escaped = escaped.replace(character, '\\' + character)

    escaped = escaped.replace('\n', '\n\n')
    return escaped


def get_confidence_interval(count, mean, std, level=0.95):
    if std == 0.0 or (count == 1 and numpy.isnan(std)):
        ci = (mean, mean)
    else:
        degrees_of_freedom = count - 1
        sem = float(std) / math.sqrt(count)

        ci = scipy.stats.t.interval(level, degrees_of_freedom, mean, sem)

    return ci


def get_error(mean, confidence_interval):
    lower = mean - confidence_interval[0]
    upper = confidence_interval[1] - mean

    assert abs(upper - lower) <= 1e-6, \
        ('Confidence interval is not symmetric: mean = {:.6f} and '
         'ci = ({:.6f}, {:.6f})'.format(mean, *confidence_interval))
    return min(lower, upper)


def get_context(responses):
    count = responses['count'].item()
    mean = responses['mean'].item()
    std = responses['std'].item()

    ci = get_confidence_interval(count, mean, std)
    error = get_error(mean, ci)

    return {
        'count': count,
        'mean': mean,
        'std': std,
        'ci': ci,
        'error': error,
    }


if '__main__' == __name__:
    parser = argparse.ArgumentParser(
        description='Create course evaluation reports')
    parser.add_argument('--debug', action='store_true',
                        help='print debugging information')
    parser.add_argument('term', action='store',
                        help='term of evaluations (e.g., spring or fall)')
    parser.add_argument('year', action='store',
                        help='year of evaluations (e.g., {})'.format(
                            date.today().year))

    args = parser.parse_args()

    data = {}

    statistics = pandas.read_csv(os.path.join('dat', 'statistics.csv'),
                                 header=None, index_col=0)
    statistics = statistics.T.to_dict(orient='list')
    for question, frequencies in statistics.items():
        data[question] = []
        for value, frequency in enumerate(frequencies):
            if value == 0:
                value = numpy.nan

            if frequency.is_integer():
                frequency = int(frequency)
                for i in range(frequency):
                    data[question].append(value)

    academy = pandas.DataFrame(data)
    if args.debug:
        print('Academy statistics:')
        with pandas.option_context('display.precision', 3):
            print(academy.agg(['count', 'mean', 'std']).T)
        print()

    enrollments = os.path.join('dat', 'enrollments.csv')
    if os.path.exists(enrollments):
        enrollments = pandas.read_csv(os.path.join('dat', 'enrollments.csv'))
    else:
        print('Missing enrollment data!\n', file=sys.stderr)
        enrollments = pandas.DataFrame(columns=['Course', 'Instructor',
                                                'Section', 'Enrollment'])

    data = pandas.read_excel(os.path.join('dat', 'evaluations.xlsx'))

    # TODO: Read from CSV file
    columns = {
      'Dept': 'Department',
      'Inst_Name': 'Instructor',
      'CourseActivities': 'Course Activities',
      'GradedEvents': 'Graded Events',
      'CourseOverall': 'Course Overall',
      'Effectiveness': 'Instructor Effectiveness',
    }
    data.rename(columns=columns, inplace=True)

    # TODO: Read from CSV file
    likert = ['Strongly Disagree', 'Disagree', 'Slightly Disagree',
              'Slightly Agree', 'Agree', 'Strongly Agree']
    quality = ['Very Poor', 'Poor', 'Fair', 'Good', 'Very Good', 'Excellent']
    frequency = ['Never', 'Rarely', 'Sometimes',
                 'Often', 'Very Often', 'Always']

    closed = {
        'Course Activities': likert,
        'Graded Events': likert,
        'Feedback': likert,
        'Course Overall': quality,
        'Effort': frequency,
        'Workload': ['1/2 hour or less',
                     'More than 1/2 hour, but less than 1 hour',
                     'More than 1 hour, but less than 2 hours',
                     'More than 2 hours, but less than 3 hours',
                     'More than 3 hours'],
        'Climate': frequency,
        'Instructor Effectiveness': quality,
    }
    open_ended = {
        'Comments': 'comments',
    }

    prompts = {
        'Course Activities': r'The course activities were effective in helping me accomplish the learning goals of this course.',  # noqa: E501
        'Graded Events': r'In this course, the graded events provided the opportunity for me to demonstrate my accomplishment of the course learning goals.',  # noqa: E501
        'Feedback': r'In this course, I received feedback that improved my ability to meet the course learning goals.',  # noqa: E501
        'Course Overall': r'Overall, this course is:',
        'Effort': r'I gave my best possible effort to learning in this course.',  # noqa: E501
        'Workload': r'On average, for every hour I spent in this class, I spent \rule{3em}{0.4pt} outside of class completing work in this course (including studying, reading, writing, doing homework or lab work, etc.)',  # noqa: E501
        'Climate': r'The instructor created a respectful, engaging learning environment for students.',  # noqa: E501
        'Instructor Effectiveness': r'Overall, my instructor is:',
        'Comments': r'Please provide any additional comments:',
    }

    funcs = ['mean', 'std', 'sem', 'count']

    def aggregate(data, by, funcs=funcs):
        invalid = set()
        for column, dtype in zip(data.columns, data.dtypes):
            if dtype in ['category', 'object', 'string']:
                invalid.add(column)
        invalid = invalid - set(by)

        return data.drop(columns=invalid).groupby(by).agg(funcs)

    courses = aggregate(data, ['Course', 'Department'], funcs)
    departments = aggregate(data, ['Department'], funcs)
    academy = academy.apply(funcs)

    environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader('./templates'),
    )

    # instructor reports
    print('Instructors')

    instructors = aggregate(data, ['Instructor', 'Course', 'Department'],
                            funcs)
    for instructor in instructors.index.unique(level='Instructor'):
        print('- ', instructor)

        subset = instructors.loc[(instructor,)]
        for course in subset.index.unique(level='Course'):
            department = subset.loc[(course,)].index.unique(level='Department')
            assert len(department) == 1
            department = department.item()

            sections = enrollments.loc[
                (enrollments['Course'] == course) &
                (enrollments['Instructor'] == instructor)]
            assert 1 <= len(sections) or 0 == len(enrollments), \
                "Missing enrollment data for {} taught by {} ".format(
                    course, instructor)

            respondents = instructors.loc[(instructor, course, department)].\
                xs('count', axis='index', level=1)
            report = {
                'instructor': instructor,
                'course': course,
                'semester': '{} {}'.format(args.term.capitalize(), args.year),
                'sections': len(sections),
                'enrollment': sections['Enrollment'].sum(),
                'responses': int(max(respondents)),
            }
            if len(enrollments) == 0:
                report['sections'] = len(
                    data.loc[(data['Course'] == course) &
                             (data['Instructor'] == instructor),
                             'Section'].unique())
                report['enrollment'] = None
            for question, responses in closed.items():
                context = {
                    'label': question,
                    'prompt': prompts[question],
                    'responses': responses,
                }

                # instructor
                course_instructors = \
                    data.loc[(data['Department'] == department) &
                             (data['Course'] == course), 'Instructor'].unique()
                assert instructor in course_instructors
                single_instructor = 1 == len(course_instructors)
                if not single_instructor:
                    responses = instructors.loc[(instructor, course,
                                                 department),
                                                question]
                    context['instructor'] = get_context(responses)

                # course
                responses = courses.loc[(course, department), question]
                context['course'] = get_context(responses)

                # department
                responses = departments.loc[(department,), question]
                context['department'] = get_context(responses)

                # academy
                responses = academy[question]
                context['academy'] = get_context(responses)

                template = environment.get_template(
                    os.path.join('instructor', 'question.tex'))
                report[question.replace(' ', '_').lower()] = \
                    template.render(context)

            comments = data.loc[(data['Department'] == department) &
                                (data['Course'] == course) &
                                (data['Instructor'] == instructor), 'Comments']
            report['comments'] = [escape(comment)
                                  for comment in comments.dropna()]

            # create report
            template = environment.get_template(
                os.path.join('instructor', 'report.tex'))

            report_path = os.path.join('reports', department, 'instructors',
                                       instructor.replace(' ', '_'),
                                       course.replace(' ', '_') + '.tex')
            create_report(report_path, template, report)
    print()

    # course reports
    print('Course')

    instructors = aggregate(data, ['Instructor', 'Department'], funcs)
    for course in courses.index.unique(level='Course'):
        print('- ', course)

        department = courses.loc[(course,)].index.unique(level='Department')
        assert len(department) == 1
        department = department.item()

        sections = enrollments.loc[enrollments['Course'] == course]
        instructors = aggregate(data.loc[data['Course'] == course],
                                ['Instructor', 'Department'], funcs)

        respondents = courses.loc[(course, department)].\
            xs('count', axis='index', level=1)
        report = {
            'course': course,
            'instructors': len(sections['Instructor'].unique()),
            'semester': '{} {}'.format(args.term.capitalize(), args.year),
            'sections': len(sections),
            'enrollment': sections['Enrollment'].sum(),
            'responses': int(max(respondents)),
        }
        if len(sections) == 0:
            report['instructors'] = len(instructors)
            report['sections'] = len(data.loc[data['Course'] == course,
                                              'Section'].unique())
            report['enrollment'] = None

        for question, responses in closed.items():
            context = {
                'label': question,
                'prompt': prompts[question],
                'responses': responses,
            }

            # course
            responses = courses.loc[(course,), question]
            context['course'] = get_context(responses)

            # department
            responses = departments.loc[(department,), question]
            context['department'] = get_context(responses)

            # academy
            responses = academy[question]
            context['academy'] = get_context(responses)

            template = environment.get_template(
                os.path.join('course', 'question.tex'))
            report[question.replace(' ', '_').lower()] = \
                template.render({**context,
                                 **{'entities': context}})

        comments = data.loc[(data['Department'] == department) &
                            (data['Course'] == course), 'Comments']
        report['comments'] = [escape(comment) for comment in comments.dropna()]

        # create report
        template = environment.get_template(
            os.path.join('course', 'report.tex'))

        report_path = os.path.join('reports', department, 'courses',
                                   course.replace(' ', '_') + '.tex')
        create_report(report_path, template, report)
    print()

    # department reports
    print('Department')

    instructors = aggregate(data, ['Instructor', 'Department'], funcs)
    for department in departments.index.unique(level='Department'):
        print('- ', department)

        for aggregation in ['Instructors', 'Courses']:
            report = {
                'courses': enrollments['Course'].unique(),
                'instructors': enrollments['Instructor'].unique(),
                'semester': '{} {}'.format(args.term.capitalize(), args.year),
                'sections': len(enrollments),
                'enrollment': enrollments['Enrollment'].sum(),
                'responses': len(data),
            }
            if len(enrollments) == 0:
                report['courses'] = data['Course'].unique()
                report['instructors'] = data['Instructor'].unique()
                report['sections'] = len(numpy.unique(data[['Course',
                                                            'Section',
                                                            'Instructor']]))
                report['enrollment'] = None

            for question, responses in closed.items():
                context = {
                    'label': question,
                    'prompt': prompts[question],
                    'responses': responses,
                }

                # instructor
                responses = instructors[question]
                context['Instructors'] = {}

                names = [instructor for instructor in
                         responses.index.unique(level='Instructor')]
                names = sorted(names,
                               key=lambda name: name.split(' ',
                                                           maxsplit=1)[-1])
                for instructor in names:
                    subset = instructors.loc[(instructor, department),
                                             question]
                    context['Instructors'][instructor] = get_context(subset)

                # course
                responses = courses[question]
                context['Courses'] = {}

                for course in responses.index.unique(level='Course'):
                    subset = courses.loc[(course, department), question]
                    context['Courses'][course] = get_context(subset)

                # department
                responses = departments.loc[(department,), question]
                context['department'] = get_context(responses)

                # academy
                responses = academy[question]
                context['academy'] = get_context(responses)

                template = environment.get_template(
                    os.path.join('department', 'question.tex'))
                report[question.replace(' ', '_').lower()] = \
                    template.render({**context,
                                     **{'entities': context[aggregation]}})

            comments = data.loc[data['Department'] == department,
                                (aggregation[:-1], 'Comments')].dropna()
            # https://stackoverflow.com/a/24370510
            comments = {key: values['Comments'].tolist()
                        for key, values in comments.groupby(aggregation[:-1])}
            if aggregation == 'Instructors':
                names = [name.split(' ', maxsplit=1)[-1]
                         for name in comments.keys()]
                comments = [item for item in comments.items()]
                comments = [item for name, item in sorted(zip(names,
                                                              comments))]
                comments = {key: values for key, values in comments}
            report['comments'] = {key: [escape(value) for value in values]
                                  for key, values in comments.items()}

            # create report
            template = environment.get_template(
                os.path.join('department', 'report.tex'))

            report_path = os.path.join('reports', department,
                                       aggregation + '.tex')
            create_report(report_path, template, report)
    print()
