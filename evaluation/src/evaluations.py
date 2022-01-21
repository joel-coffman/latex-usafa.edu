#!/usr/bin/env python

import math
import os
import shutil

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

    with open(path, 'w') as fp:
        fp.write(template.render(context))

    shutil.copy('./templates/Makefile',
                os.path.join(directory, 'Makefile'))


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


def escape(value):
    escaped = value
    for character in ['\\', '&', '#', '_', '$']:
        escaped = escaped.replace(character, '\\' + character)

    special = {
        '<': '\\textless',
        '>': '\\textgreater',
        '\'': '\\textquotesingle',
        '"': '\\textquotedbl',
        '-': '-',
    }
    for character, replacement in special.items():
        escaped = escaped.replace(character, replacement + '{}')

    escaped = escaped.replace('\n', '\n\n')
    return escaped


semester = 'Fall 2021'


data = {}

# TODO: Read data from CSV file
responses = {
    'Course Activities': [109, 193, 273, 362, 1459, 4321, 3474],
    'Graded Events': [315, 209, 255, 459, 1582, 4099, 3272],
    'Feedback': [308, 209, 323, 558, 1748, 3726, 3319],
    'Course Overall': [456, 190, 399, 1132, 2545, 2764, 2705],
    'Effort': [483, 33, 152, 786, 2238, 3466, 3033],
    'Workload': [477, 1463, 3051, 3529, 1256, 415],
    'Climate': [628, 22, 56, 215, 684, 1493, 7093],
    'Instructor Effectiveness': [634, 95, 217, 556, 1263, 2221, 5205],
}
for question, frequencies in responses.items():
    data[question] = []
    for value, frequency in enumerate(frequencies):
        if value == 0:
            value = numpy.nan

        for i in range(frequency):
            data[question].append(value)

academy = pandas.DataFrame(data)


enrollments = pandas.read_csv(os.path.join('dat', 'enrollments.csv'))


data = pandas.read_csv(os.path.join('dat', 'evaluations.csv'))

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
frequency = ['Never', 'Rarely', 'Sometimes', 'Often', 'Very Often', 'Always']

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
courses = data.groupby(['Course', 'Department']).agg(funcs)
departments = data.groupby(['Department']).agg(funcs)
academy = academy.apply(funcs)

environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader('./templates'),
)

# instructor reports
instructors = data.groupby(['Instructor', 'Course', 'Department']).agg(funcs)
for instructor in instructors.index.unique(level='Instructor'):
    print(instructor)

    subset = instructors.loc[(instructor,)]
    for course in subset.index.unique(level='Course'):
        print('  {}'.format(course))

        department = subset.loc[(course,)].index.unique(level='Department')
        assert len(department) == 1
        department = department.item()

        sections = enrollments.loc[(enrollments['Course'] == course) &
                                   (enrollments['Instructor'] == instructor)]
        assert 1 <= len(sections), "Missing enrollment data!"

        respondents = instructors.loc[(instructor, course, department)].\
            xs('count', axis='index', level=1)
        report = {
            'instructor': instructor,
            'course': course,
            'semester': semester,
            'sections': len(sections),
            'enrollment': sections['Enrollment'].sum(),
            'responses': int(max(respondents)),
        }
        for question, responses in closed.items():
            print('    ' + question)

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
                responses = instructors.loc[(instructor, course, department),
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

            # print summary
            aggregations = ([] if single_instructor else ['instructor'] +
                            ['course', 'department', 'academy'])
            for aggregation in aggregations:
                mean = context[aggregation]['mean']
                ci = context[aggregation]['ci']
                error = mean - ci[0]

                print('      {:12s} {:.3f} +- {:.3f}'.format(aggregation,
                                                             mean, error))

            template = environment.get_template(
                os.path.join('instructor', 'question.tex'))
            report[question.replace(' ', '_').lower()] = \
                template.render(context)

        comments = data.loc[(data['Department'] == department) &
                            (data['Course'] == course) &
                            (data['Instructor'] == instructor), 'Comments']
        report['comments'] = [escape(comment) for comment in comments.dropna()]

        # create report
        template = environment.get_template(
            os.path.join('instructor', 'report.tex'))

        report_path = os.path.join('reports', 'instructors',
                                   instructor.replace(' ', '_'),
                                   course.replace(' ', '_') + '.tex')
        create_report(report_path, template, report)

# course reports
instructors = data.groupby(['Instructor', 'Department']).agg(funcs)
for course in courses.index.unique(level='Course'):
    print(course)

    department = courses.loc[(course,)].index.unique(level='Department')
    assert len(department) == 1
    department = department.item()

    sections = enrollments.loc[enrollments['Course'] == course]
    instructors = data.loc[data['Course'] == course].\
        groupby(['Instructor', 'Department']).agg(funcs)

    respondents = courses.loc[(course, department)].\
        xs('count', axis='index', level=1)
    report = {
        'course': course,
        'instructors': len(sections['Instructor'].unique()),
        'semester': semester,
        'sections': len(sections),
        'enrollment': sections['Enrollment'].sum(),
        'responses': int(max(respondents)),
    }

    for question, responses in closed.items():
        print('  ' + question)

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

        # print summary
        for aggregation in ['course', 'department', 'academy']:
            mean = context[aggregation]['mean']
            ci = context[aggregation]['ci']
            error = mean - ci[0]

            print('      {:12s} {:.3f} +- {:.3f}'.format(aggregation,
                                                         mean, error))

        template = environment.get_template(
            os.path.join('course', 'question.tex'))
        report[question.replace(' ', '_').lower()] = \
            template.render({**context,
                             **{'entities': context[aggregation]}})

    comments = data.loc[(data['Department'] == department) &
                        (data['Course'] == course), 'Comments']
    report['comments'] = [escape(comment) for comment in comments.dropna()]

    # create report
    template = environment.get_template(
        os.path.join('course', 'report.tex'))

    report_path = os.path.join('reports', 'courses',
                               course.replace(' ', '_') + '.tex')
    create_report(report_path, template, report)

# department reports
instructors = data.groupby(['Instructor', 'Department']).agg(funcs)
for department in departments.index.unique(level='Department'):
    print(department)

    for aggregation in ['Instructors', 'Courses']:
        print('  ' + aggregation)

        report = {
            'courses': enrollments['Course'].unique(),
            'instructors': enrollments['Instructor'].unique(),
            'semester': semester,
            'sections': len(enrollments),
            'enrollment': enrollments['Enrollment'].sum(),
            'responses': len(data),
        }

        for question, responses in closed.items():
            print('    ' + question)

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
                           key=lambda name: name.split(' ', maxsplit=1)[-1])
            for instructor in names:
                subset = instructors.loc[(instructor, department), question]
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

            # print summary
            for entity in context[aggregation]:
                values = context[aggregation][entity]

                mean = values['mean']
                ci = values['ci']
                error = mean - ci[0]

                print('      {:20s} {:.3f} +- {:.3f}'.format(entity,
                                                             mean, error))

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
            comments = [item for name, item in sorted(zip(names, comments))]
            comments = {key: values for key, values in comments}
        report['comments'] = {key: [escape(value) for value in values]
                              for key, values in comments.items()}

        # create report
        template = environment.get_template(
            os.path.join('department', 'report.tex'))

        report_path = os.path.join('reports', 'departments', department,
                                   aggregation + '.tex')
        create_report(report_path, template, report)
