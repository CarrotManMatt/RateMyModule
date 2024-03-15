"""Contains a selection of graph generating functions."""
from collections.abc import Sequence

__all__: Sequence[str] = (
    "assessment_quality_bar_graph",
    "teaching_quality_bar_graph",
    "difficulty_rating_bar_graph",
    "overall_rating_bar_graph",
)

from io import StringIO
from math import ceil
from typing import Final

import matplotlib.pyplot as plt
import numpy as np
from django import template
from matplotlib.patches import FancyBboxPatch

from ratemymodule.models import Module

register = template.Library()


def return_test_svg() -> str:
    """Return a basic test graph."""
    fig, ax = plt.subplots()
    x_points = np.array([0, 1, 2, 3, 4])
    y_points = np.array([1, 2, 3, 4, 5])
    plt.plot(x_points, y_points)
    plt.xlabel("Time")
    plt.ylabel("Clicks")
    image_format = "svg"
    string_me_along = StringIO()
    fig.savefig(string_me_along, format=image_format)
    return string_me_along.getvalue()


def custom_line_graph(x__points: list[int], y__points: list[int], x_label: str, y_label: str) -> str:  # noqa: E501
    """Return a custom line graph of x points against y points."""
    if len(x__points) != len(y__points):
        LENGTH_NOT_EQUAL_MESSAGE: Final[str] = "Length of x points and y points not equal"
        raise ValueError(LENGTH_NOT_EQUAL_MESSAGE)
    fig, ax = plt.subplots()
    x_points = np.array(x__points)
    y_points = np.array(y__points)
    plt.plot(x_points, y_points)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    out_string = StringIO()
    fig.savefig(out_string, format="svg")
    return out_string.getvalue()


def rating_bar_graph(array_of_in_ratings: list[int], title: str, _bar_color: str, _label_color: str) -> str:  # noqa: E501
    """Make a bar graph outputted to string svg."""
    label_color = _label_color

    fig, ax = plt.subplots()
    rating_levels = [1, 2, 3, 4, 5]

    # transform input to normalized percentages
    total = 0
    for counter in range(5):
        total = total + array_of_in_ratings[counter]

    if total == 0:
        return ""

    array_of_ratings: list[float] = [0, 0, 0, 0, 0]
    for counter in range(5):
        array_of_ratings[counter] = 0.0025 + ((array_of_in_ratings[counter] / total) * 100)
        # adds small offset to bars, so they don't become weird after curving ends

    rects = ax.barh(rating_levels, array_of_ratings,
                    color=_bar_color, label=array_of_in_ratings  # noqa: COM812
                    )

    # make curved corners on bar ends
    new_patches = []
    for patch in reversed(ax.patches):
        bb = patch.get_bbox()
        color = patch.get_facecolor()
        p_bbox = FancyBboxPatch((bb.xmin, bb.ymin), abs(bb.width),
                                abs(bb.height),
                                boxstyle="round,pad=-0.0080,rounding_size=0.1",
                                ec="none", fc=color,
                                mutation_aspect=4,
                                )
        patch.remove()
        new_patches.append(p_bbox)
    for patch in new_patches:
        ax.add_patch(patch)

    # remove frame lines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # finishing touches
    y_pos = np.arange(6)
    rating_levels_ticks = ["", "1★", "2★", "3★", "4★", "5★"]
    ax.set_yticks(y_pos, labels=rating_levels_ticks, color=label_color, weight="bold")
    ax.set_title(title, color=label_color, weight="bold", loc="left")
    ax.set_xlabel("Percent Of Reviews", color=label_color, weight="bold")
    for tick in ax.get_xticklabels():
        tick.set_fontweight("bold")

    # attach labels on the bar's tips
    # if bar less than 40% value of largest bar put text outside it
    array_of_bar_labels = ["", "", "", "", ""]
    for counter in range(5):
        if array_of_in_ratings[counter] == 1:
            array_of_bar_labels[counter] = "(1 Review)"
        elif array_of_in_ratings[counter] == 0:
            array_of_bar_labels[counter] = "(0 Reviews)"
        else:
            array_of_bar_labels[counter] = f"({array_of_in_ratings[counter]} Reviews)"

    forty_max = ceil(max(array_of_in_ratings) * 0.4)
    inside_of_bar_texts = [p if p >= forty_max
                           else "" for p in array_of_in_ratings
                           ]
    for counter in range(5):
        if inside_of_bar_texts[counter] != "":
            inside_of_bar_texts[counter] = array_of_bar_labels[counter]

    out_of_bar_texts = [p if p < forty_max
                        else "" for p in array_of_in_ratings
                        ]
    for counter in range(5):
        if out_of_bar_texts[counter] != "":
            out_of_bar_texts[counter] = array_of_bar_labels[counter]

    ax.bar_label(rects, out_of_bar_texts, padding=5, color=label_color, fontweight="bold")
    # has white text on purple always
    ax.bar_label(rects, inside_of_bar_texts, padding=-75, color="#f0f0f0", fontweight="bold")

    # recolour axis to taste
    ax.tick_params(axis="x", colors=label_color)
    ax.tick_params(axis="y", length=0)
    # set size to fit only my screen
    fig.set_size_inches(3.1, 4)

    # outputting it to string
    image_format = "svg"
    out_string = StringIO()
    fig.savefig(out_string, format=image_format, transparent=True, bbox_inches="tight", dpi=80)
    return out_string.getvalue()


def overall_rating_bar_graph(module: Module, button_colour: str, text_colour: str) -> str:
    """Use rating_bar_graph to generate a bar graph of overall rating."""
    title = "Overall Rating"
    bar_colour = f"#{button_colour}"
    label_colour = f"#{text_colour}"
    data: list[int] = []

    for counter in range(1, 6):
        data.insert(counter, len(module.post_set.filter(overall_rating=counter)))
    return rating_bar_graph(data, title, bar_colour, label_colour)


def difficulty_rating_bar_graph(module: Module, button_colour: str, text_colour: str) -> str:
    """Use rating_bar_graph to generate a bar graph of difficulty rating."""
    title = "Difficulty Rating"
    bar_colour = f"#{button_colour}"
    label_colour = f"#{text_colour}"
    data: list[int] = []
    for counter in range(1, 6):
        data.insert(counter, len(module.post_set.filter(difficulty_rating=counter)))
    return rating_bar_graph(data, title, bar_colour, label_colour)


def teaching_quality_bar_graph(module: Module, button_colour: str, text_colour: str) -> str:
    """Use rating_bar_graph to generate a bar graph of teaching rating."""
    title = "Teaching Quality"
    bar_colour = f"#{button_colour}"
    label_colour = f"#{text_colour}"
    data: list[int] = []
    for counter in range(1, 6):
        data.insert(counter, len(module.post_set.filter(teaching_rating=counter)))
    return rating_bar_graph(data, title, bar_colour, label_colour)


def assessment_quality_bar_graph(module: Module, button_colour: str, text_colour: str) -> str:
    """Use rating_bar_graph to generate a bar graph of assessment rating."""
    title = "Assessment Quality"
    bar_colour = f"#{button_colour}"
    label_colour = f"#{text_colour}"
    data: list[int] = []
    for counter in range(1, 6):
        data.insert(counter, len(module.post_set.filter(assessment_rating=counter)))
    return rating_bar_graph(data, title, bar_colour, label_colour)
