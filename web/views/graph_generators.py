"""Contains a selection of graph generating functions for RateMyModule."""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "assessment_quality_bar_graph",
    "teaching_quality_bar_graph",
    "difficulty_rating_bar_graph",
    "overall_rating_bar_graph",
)

import datetime
from calendar import monthrange
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
    flag_nodata = False

    fig, ax = plt.subplots()
    rating_levels = [1, 2, 3, 4, 5]

    # transform input to normalized percentages
    total = sum(array_of_in_ratings)

    array_of_ratings: list[float] = [0, 0, 0, 0, 0]
    if total == 0:
        flag_nodata = True

    else:
        for counter in range(5):
            array_of_ratings[counter] = 0.0025 + ((array_of_in_ratings[counter] / total) * 100)
            # adds small offset to bars, so they don't become weird after curving ends

    rects = ax.barh(rating_levels, array_of_ratings,
                    color=_bar_color, label=array_of_in_ratings,
                    )

    # make curved corners on bar ends
    if not flag_nodata:
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
    # if bar less than 40% value of the largest bar put the text outside it
    array_of_bar_labels = sb_format_reviews_string(array_of_in_ratings)

    out_of_bar_texts, inside_of_bar_texts = decide_in_or_out_of_bars(
        array_of_in_ratings, array_of_bar_labels,
    )

    if flag_nodata:
        out_of_bar_texts[3] = "No posts = (\n be the first to \nRateThisModule!"

    ax.bar_label(rects, out_of_bar_texts, padding=5, color=label_color,
                 fontweight="light",
                 )
    # has white text on purple always
    if flag_nodata:
        ax.bar_label(
            rects, inside_of_bar_texts, padding=-50, color=label_color, fontweight="light",
        )
    else:
        ax.bar_label(
            rects, inside_of_bar_texts, padding=-75, color="#f0f0f0", fontweight="light",
            )

    # recolour axis to taste
    ax.tick_params(axis="x", colors=label_color)
    ax.tick_params(axis="y", length=0)
    # set size to fit only my screen
    fig.set_size_inches(3.1, 4)

    # outputting it to string
    image_format = "svg"
    out_string = StringIO()
    fig.savefig(out_string, format=image_format, transparent=True, bbox_inches="tight", dpi=80)
    plt.close(fig)
    return out_string.getvalue()


def sb_format_reviews_string(array_of_in_ratings: list[int]) -> list[str]:
    array_of_bar_labels: list[str] = ["", "", "", "", ""]
    for counter in range(5):
        if array_of_in_ratings[counter] == 1:
            array_of_bar_labels[counter] = "(1 Review)"
        elif array_of_in_ratings[counter] == 0:
            array_of_bar_labels[counter] = "(0 Reviews)"
        else:
            array_of_bar_labels[counter] = f"({array_of_in_ratings[counter]} Reviews)"
    return array_of_bar_labels


def decide_in_or_out_of_bars(array_of_in_ratings: list[int], array_of_bar_labels: list[str]) -> tuple[list[str], list[str]]:  # noqa: E501
    # if bar less than 40% value of the largest bar, then put the text outside it
    forty_max = ceil(max(array_of_in_ratings) * 0.5)
    inside_of_bar_texts: list[str] = [
        "x" if p >= forty_max else ""
        for p
        in array_of_in_ratings
    ]
    for counter in range(5):
        if inside_of_bar_texts[counter] != "":
            inside_of_bar_texts[counter] = array_of_bar_labels[counter]

    out_of_bar_texts: list[str] = ["x" if p < forty_max else "" for p in array_of_in_ratings]
    for counter in range(5):
        if out_of_bar_texts[counter] != "":
            out_of_bar_texts[counter] = array_of_bar_labels[counter]

    return out_of_bar_texts, inside_of_bar_texts


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


def advanced_analytics_graph(module: Module, difficulty_rating: bool, assessment_quality: bool, teaching_rating: bool, overall_rating: bool, start_year: int, end_year: int) -> str:  # noqa: E501, FBT001, PLR0915
    """Plot a custom line graph for the analytics modal."""
    """
    This function is "too complex" according to ruff,
    sadly I (tom) can't reasonably untangle it anymore than it is
    This function ignores: passing bool as parameter, line too long and function too complex
    """

    # input sanitization, no reviews before 1900, no invalid date settings, no massive ranges
    errors = validate_dates(start_year, end_year)
    if errors != "":
        return errors

    now = datetime.datetime.now(tz=datetime.UTC)

    end_year = end_year+1

    date_list, guide_bar, x_axis = aa_set_up_axis(start_year, end_year)

    guide_bar.pop(1)
    guide_bar[-1] = 1  # type: ignore[call-overload] # HACK: Use incorrect indexing type

    label_color = "#aaaaaa"
    fig, ax = plt.subplots(sharex=True, sharey=True)

    ax.plot(x_axis, guide_bar, visible=False)
    background_line_colour = "#888888"

    if overall_rating:
        ax.plot(get_module_averages(
            start_year, end_year, module, "overall_rating"),
            label="Overall Rating",
        )

    if difficulty_rating:
        ax.plot(get_module_averages(
            start_year, end_year, module, "difficulty_rating"),
            label="Difficulty Rating",
        )

    if teaching_rating:
        ax.plot(get_module_averages(
            start_year, end_year, module, "teaching_rating"),
            label="Teaching Quality",
        )

    if assessment_quality:
        ax.plot(get_module_averages(
            start_year, end_year, module, "assessment_rating"),
            label="Assessment Quality",
        )

    y_pos = np.arange(start=1, stop=5.5, step=0.5)
    rating_levels_ticks = [
        "1★", "1.5★", "2★", "2.5★",
        "3★", "3.5★", "4★", "4.5★", "5★"]
    if end_year-1 == now.year:
        title = (f"Graph of {module.name},\nfrom 1/1/{start_year} to "
                 f"{now.day}/{now.month}/"
                 f"{now.year}")
    else:
        title = f"Graph of {module.name},\nfrom 1/1/{start_year} to 31/12/{end_year-1}"
    ax.set_yticks(y_pos, labels=([""]*9))
    ax.set_title(title, color=label_color, weight="bold", loc="left")
    ax.margins(x=0)

    for tick in ax.get_xticklabels():
        tick.set_fontweight("bold")

    ax.tick_params(axis="x", colors=label_color)
    ax.set_ylim([0.5, 5.5])

    y_value: float = 1
    i = 0
    ENDCAP: float = 5.5
    while y_value != ENDCAP:
        ax.axhline(y=y_value, color=background_line_colour, zorder=0, lw=0.5)
        ax.text(-0.5, y_value, rating_levels_ticks[i],
                ha="right", va="center", color=label_color, weight="bold")
        y_value += 0.5
        i += 1

    if len(date_list) > 12:
        length_of_dates = len(date_list)
        x_ticks = [""] * length_of_dates

        div = int(length_of_dates / 12)
        divarray = np.arange(start=0, stop=len(date_list), step=div)

        for value in divarray:
            x_ticks[value] = date_list[value]

        x_ticks[length_of_dates-2] = ""
        x_ticks[length_of_dates-1] = date_list[length_of_dates-1]
        ax.set_xticks(
            np.arange(length_of_dates), labels=x_ticks, color=label_color,
            rotation=-45, rotation_mode="anchor", horizontalalignment="left",
            verticalalignment="center",
        )

    else:
        ax.set_xticks(
            np.arange(len(date_list)), labels=date_list, color=label_color, rotation=-45,
            rotation_mode="anchor", horizontalalignment="left",
            verticalalignment="center",
        )
    # legend processing
    ax.legend(labelcolor="#aaaaaa", facecolor="#000001", edgecolor="#000002")

    fig.set_size_inches(6.5, 4.35)
    image_format = "svg"
    out_string = StringIO()
    fig.savefig(
        out_string, format=image_format, transparent=True, bbox_inches="tight", dpi=80)
    plt.close(fig)  # delete the figure
    return out_string.getvalue()


def validate_dates(start_year: int, end_year: int) -> str:
    errors = ""
    now = datetime.datetime.now(tz=datetime.UTC)
    if start_year > end_year:
        errors += "Invalid year parameters, please check your inputs.\n"
    if start_year < 1900:
        errors += "Earliest date option is 1900.\n"
    if end_year-start_year > 50:
        errors += "Date range too large, try focusing your query.\n"
    if end_year > now.year:
        errors += "End date is in the future.\n"
    return errors


def aa_set_up_axis(start_year: int, end_year: int) -> tuple[list[str], list[None], list[int]]:
    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]
    i = 0
    date_list: list[str] = []
    guide_bar: list[None] = [None]
    x_axis: list[int] = []
    now = datetime.datetime.now(tz=datetime.UTC)
    for counter in range(start_year, end_year):  # set up the month labels
        if counter == now.year:
            for counter2 in range(now.month):
                date_list.append(str(months[counter2] + str(counter)))
                guide_bar.append(None)
                x_axis.append(i)
                i += 1
            break

        for counter2 in range(12):
            date_list.append(f"{months[counter2]}{counter}")
            guide_bar.append(None)
            x_axis.append(i)
            i += 1
    return date_list, guide_bar, x_axis


def get_module_averages(start_year: int, end_year: int, module: Module, attribute: str) -> list[float]:  # noqa: E501
    """Get the average of each month's reviews for a module in a specified date range."""
    set_of_averages: list[float] = []
    for year in range(start_year, end_year):
        if year == datetime.datetime.now(tz=datetime.UTC).date().year:
            for month in range(
                    1, datetime.datetime.now(tz=datetime.UTC).date().month+1,
            ):
                start_band = datetime.datetime(year, month, 1).astimezone(
                    tz=datetime.UTC,
                )
                end_band = datetime.datetime(
                    year, month, monthrange(year, month)[1]).astimezone(
                    tz=datetime.UTC,
                )
                # gets last day of the month, normalize to timezone

                this_months_reviews = [
                    getattr(post, attribute) for post in module.post_set.all()
                    if start_band <= post.date_time_created <= end_band
                ]

                if this_months_reviews:
                    set_of_averages.append(sum(this_months_reviews) / len(this_months_reviews))
                else:
                    set_of_averages.append(0.55)
            return set_of_averages

        for month in range(1, 13):
            start_band = datetime.datetime(year, month, 1).astimezone(tz=None)
            end_band = datetime.datetime(
                year, month, monthrange(year, month)[1]).astimezone(tz=None)
            # gets last day of the month, normalize to timezone

            this_months_reviews = [
                getattr(post, attribute) for post in module.post_set.all()
                if start_band <= post.date_time_created <= end_band
            ]

            if this_months_reviews:
                set_of_averages.append(sum(this_months_reviews) / len(this_months_reviews))
            else:
                set_of_averages.append(0.55)
    return set_of_averages
