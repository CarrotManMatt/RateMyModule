"""contains a selection of functions to populate the database with random data"""

import datetime
import random

import numpy as np

from ratemymodule.models import Course, Post, User


def populate_database() -> None:
    lazy_stop = False   # set True if you wanna just view graphs
    if lazy_stop:
        return

    i = 0  # if you run function more than once, update this to highest user, or it will break
    YEARS_BACK = 5   # how many years of data
    REVIEWS_PER_MONTH = 5  # how many reviews per month of said years
    CURRENT_YEAR = 2025  # what year to start and work back from
    course = Course.objects.all()[0]  # for first course in database
    for module in course.module_set.all():
        trends: list[list[int]] = []
        for counter in range(4):
            trends.append(generate_quality_trend(YEARS_BACK, REVIEWS_PER_MONTH))
        for year_counter in range(CURRENT_YEAR-YEARS_BACK, CURRENT_YEAR):
            for month in range(12):
                time_stamp = datetime.datetime(
                    year_counter, month+1,
                    1, 1, 1, 1,
                ).astimezone(tz=None)
                for review in range(REVIEWS_PER_MONTH):
                    tempUser = User.objects.create_user(email=f"filler{i}@test.bham.ac.uk")
                    tempUser.enrolled_course_set.add(course)
                    tempPost = Post.objects.create(
                        module=module, user=tempUser,
                        overall_rating=trends[0].pop(0),
                        difficulty_rating=trends[1].pop(0),
                        assessment_rating=trends[2].pop(0),
                        teaching_rating=trends[3].pop(0),
                        academic_year_start=year_counter
                    )
                    tempPost.date_time_created = time_stamp
                    tempUser.save()
                    tempPost.save()
                    i += 1
                # don't need names, password, just need a email for uni, course


def generate_trend_up(num_samples: int, _start: float) -> list[int]:
    if _start < 4:
        _stop = _start + random.uniform(0.25, _start+1)
    else:
        _stop = _start

    data = np.linspace(start=_start, stop=_stop, num=num_samples)
    output: list[int] = []
    for number in data:
        vary = random.randint(0, 4)
        if vary < 3:
            number = number + random.uniform(0, 1)
        else:
            number = number + random.uniform(-1, 0)

        if number > 5:
            number = 5
        elif number < 1:
            number = 1
        output.append(int(number))
    return output


def generate_trend_down(num_samples: int, _start: float) -> list[int]:
    if _start > 2:
        _stop = _start - random.uniform(0.25, _start-1)
    else:
        _stop = _start

    data = np.linspace(start=_start, stop=_stop, num=num_samples)
    output: list[int] = []
    for number in data:
        vary = random.randint(0, 4)
        if vary < 3:
            number = number + random.uniform(-1, 0)
        else:
            number = number + random.uniform(0, 1)
        if number > 5:
            number = 5
        elif number < 1:
            number = 1
        output.append(int(number))
    return output


def generate_level_trend(num_samples: int, _start: float) -> list[int]:
    data = np.linspace(start=_start, stop=_start, num=num_samples)
    output: list[int] = []
    for number in data:
        vary = random.randint(0, 4)
        if vary <= 2:
            number = number + random.uniform(-1, 1)
        if number > 5:
            number = 5
        elif number < 1:
            number = 1
        output.append(int(number))

    return output


def generate_random_trend(num_samples: int) -> list[int]:
    output: list[int] = []
    for counter in range(num_samples):
        output.append(random.randint(1, 5))
    return output


def generate_quality_trend(years_back: int, reviews_per_month: int) -> list[int]:
    num_samples = (reviews_per_month * 12 * years_back)
    min_segment = reviews_per_month * years_back
    max_segment = reviews_per_month * 4 * years_back
    TREND_TYPES = [
        generate_trend_up, generate_trend_down, generate_trend_up,  # generate_trend_down,
        generate_level_trend,  # generate_level_trend,  # generate_random_trend
    ]
    TREND_DOWN = [
        generate_trend_down, generate_level_trend, generate_trend_down,
    ]
    TREND_UP = [
        generate_trend_up, generate_level_trend, generate_trend_up,
    ]
    data = []
    segment: int
    start = random.uniform(1, 5)
    running = True
    while running:
        segment = random.randint(min_segment, max_segment)
        if segment > num_samples:
            if 4 > start > 2:
                data.extend(random.choice(TREND_TYPES)(num_samples, start))
            elif start >= 4:
                data.extend(random.choice(TREND_DOWN)(num_samples, start))
            else:
                data.extend(random.choice(TREND_UP)(num_samples, start))
            running = False
        else:
            if 4 > start > 2:
                data.extend(random.choice(TREND_TYPES)(segment, start))
            elif start >= 4:
                data.extend(random.choice(TREND_DOWN)(segment, start))
            else:
                data.extend(random.choice(TREND_UP)(segment, start))
            num_samples -= segment
            start = data[-1]
    return data
