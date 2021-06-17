#!/usr/bin/env python

import math
import os
import shutil

import jinja2
import numpy
import pandas
import scipy.stats


def get_confidence_interval(count, mean, std, level=0.95):
    if std == 0.0:
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


semester = 'Spring 2021'


data = {}

responses = {
    'Course Activities': [0, 178, 314, 445, 1893, 3912, 3052],
    'Graded Events': [1, 226, 335, 511, 1978, 3708, 3035],
    'Feedback': [1, 259, 382, 650, 2165, 3232, 3105],
    'Course Overall': [1, 241, 423, 1147, 2663, 2669, 2650],
    'Effort': [0, 48, 147, 786, 2747, 3285, 2781],
    'Workload': [0, 925, 2472, 3732, 2088, 577],
    'Climate': [0, 61, 99, 341, 1283, 1445, 6565],
    'Instructor Overall': [1, 117, 200, 535, 1672, 2196, 5073],
}
for question, frequencies in responses.items():
    data[question] = []
    for value, frequency in enumerate(frequencies):
        if value == 0:
            value = numpy.nan

        for i in range(frequency):
            data[question].append(value)

academy = pandas.DataFrame(data)


data = pandas.read_csv(os.path.join('dat', 'evaluations.csv'))

columns = {
  'Dept': 'Department',
  'InstName': 'Instructor',
  'Course_Activites': 'Course Activities',
  'Graded_Events': 'Graded Events',
  'Course_Overall': 'Course Overall',
  'Instructor_Overall': 'Instructor Overall',
}
data.rename(columns=columns, inplace=True)


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
    'Instructor Overall': quality,
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
    'Workload': r'On average, for every hour I spent in this class, I spent \rule{3em}{0.4pt} outside of class completing work in this course (including studying, reading, writing, doing homework or lab work, etc.',  # noqa: E501
    'Climate': r'The instructor created a respectful, engaging learning environment for students.',  # noqa: E501
    'Instructor Overall': r'Overall, my instructor is:',
    'Comments': r'Please provide any additional comments:',
}


funcs = ['mean', 'std', 'sem', 'count']
instructors = data.groupby(['Instructor', 'Course', 'Department']).agg(funcs)
courses = data.groupby(['Course', 'Department']).agg(funcs)
departments = data.groupby(['Department']).agg(funcs)
academy = academy.apply(funcs)

environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader('./templates'),
)

for instructor in instructors.index.unique(level='Instructor'):
    print(instructor)

    subset = instructors.loc[(instructor,)]
    for course in subset.index.unique(level='Course'):
        print('  {}'.format(course))

        department = subset.loc[(course,)].index.unique(level='Department')
        assert len(department) == 1
        department = department.item()

        respondents = instructors.loc[(instructor, course, department)].\
            xs('count', axis='index', level=1)
        report = {
            'instructor': instructor,
            'course': course,
            'semester': semester,
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

            template = environment.get_template('question.tex')
            report[question.replace(' ', '_').lower()] = \
                template.render(context)

        comments = data.loc[(data['Department'] == department) &
                            (data['Course'] == course) &
                            (data['Instructor'] == instructor), 'Comments']
        report['comments'] = [escape(comment) for comment in comments.dropna()]

        # create report
        template = environment.get_template('instructor.tex')

        directory = os.path.join('./reports', instructor.replace(' ', '_'))
        if not os.path.isdir(directory):
            os.mkdir(directory)

        with open(os.path.join(directory,
                               '{}.tex'.format(course.replace(' ', '_'))),
                  'w') as fp:
            fp.write(template.render(report))

        shutil.copy('./templates/Makefile',
                    os.path.join(directory, 'Makefile'))

    # break
