# mypy: ignore-errors

from io import StringIO

import matplotlib.pyplot as plt
import numpy as np
from django import template
from matplotlib.patches import FancyBboxPatch

from ratemymodule.models import Post

register = template.Library()


def return_test_svg():
    fig, ax = plt.subplots()
    x_points = np.array([0, 1, 2, 3, 4, 5])
    y_points = np.array([1, 2, 3, 4, 5, 6])
    plt.plot(x_points, y_points)
    plt.xlabel("Time")
    plt.ylabel("Clicks")
    image_format = 'svg'
    string_me_along = StringIO()
    fig.savefig(string_me_along, format=image_format)
    return string_me_along


def custom_line_graph(x__points: list[int], y__points: list[int], x_label: str, y_label: str):
    if len(x__points) != len(y__points):
        raise ValueError("Length of x points and y points not equal")
    fig, ax = plt.subplots()
    x_points = np.array(x__points)
    y_points = np.array(y__points)
    plt.plot(x_points, y_points)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    image_format = 'svg'
    out_string = StringIO()
    fig.savefig(out_string, format=image_format)
    return out_string


def rating_bar_graph(array_of_ratings: list[int], title: str, _color):
    """make a bar graph outputted to string svg"""
    label_color = '#ffffff'

    fig, ax = plt.subplots()
    rating_levels = [0, 1, 2, 3, 4, 5]

    # transform input to normalized percentages
    total = 0
    for counter in range(0, 6):
        total = total + array_of_ratings[counter]

    if total == 0:
        return ""

    for counter in range(0, 6):
        array_of_ratings[counter] = 0.0025 + ((array_of_ratings[counter] / total) * 100)
        # adds small offset to bars, so they don't become weird after curving ends

    ax.barh(rating_levels, array_of_ratings, color=_color)

    # make curved corners on bar ends
    new_patches = []
    for patch in reversed(ax.patches):
        bb = patch.get_bbox()
        color = patch.get_facecolor()
        p_bbox = FancyBboxPatch((bb.xmin, bb.ymin), abs(bb.width),
                                abs(bb.height),
                                boxstyle="round,pad=-0.0080,rounding_size=0.1",
                                ec="none", fc=color,
                                mutation_aspect=4
                                )
        # fixme-Tom: some cretin decided curvature is proportional to size ^
        patch.remove()
        new_patches.append(p_bbox)
    for patch in new_patches:
        ax.add_patch(patch)

    # remove frame lines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # finishing touches
    y_pos = np.arange(6)
    rating_levels_ticks = ["0★", "1★", "2★", "3★", "4★", "5★"]
    ax.set_yticks(y_pos, labels=rating_levels_ticks, color=label_color, weight="bold")
    ax.set_title(title, color=label_color, weight='bold', loc='left')
    ax.set_xlabel('Percent Of Reviews', color=label_color, weight='bold')
    for tick in ax.get_xticklabels():
        tick.set_fontweight('bold')

    # recolour axis to taste
    ax.tick_params(axis='x', colors=label_color)

    # set size to fit only my screen #TODO tom - make graph dynamically scale
    fig.set_size_inches(3.1, 4)

    # outputting it to string
    image_format = 'svg'
    out_string = StringIO()
    fig.savefig(out_string, format=image_format, transparent=True, bbox_inches='tight', dpi=80)
    return out_string.getvalue()


def overall_rating_bar_graph() -> str:
    title = "Overall Rating"
    color = '#7f4fd9'
    data = []

    for counter in range(0, 6):
        data.insert(counter, len(Post.objects.filter(overall_rating=counter)))

    return rating_bar_graph(data, title, color)


def difficulty_rating_bar_graph() -> str:
    title = "Difficulty Rating"
    color = '#7f4fd9'  # f060df
    data = []
    for counter in range(0, 6):
        data.insert(counter, len(Post.objects.filter(difficulty_rating=counter)))
    return rating_bar_graph(data, title, color)


def teaching_quality_bar_graph() -> str:
    title = "Teaching Quality"
    color = '#7f4fd9'  # f060df
    data = []
    for counter in range(0, 6):
        data.insert(counter, len(Post.objects.filter(teaching_rating=counter)))
    return rating_bar_graph(data, title, color)


def assessment_quality_bar_graph() -> str:
    title = "Assessment Quality"
    color = '#7f4fd9'  # f060df
    data = []
    for counter in range(0, 6):
        data.insert(counter, len(Post.objects.filter(assessment_rating=counter)))
        # data.insert(counter, np.random.randint(1, 100))
    return rating_bar_graph(data, title, color)
