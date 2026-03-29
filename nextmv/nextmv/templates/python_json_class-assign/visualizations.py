"""
Visual assets generation for the school class assignment problem.
Creates Nextmv-compatible Plotly visualizations.
"""

from typing import Any


def _build_hover_text(
    cls: dict[str, Any],
    level: str,
    assignment_lookup: dict[str, list[dict[str, Any]]],
) -> str:
    """
    Build the hover text for a class marker in the layout visualization.

    Parameters
    ----------
    cls : dict[str, Any]
        Dictionary containing class data.  Expected keys include ``id``,
        ``name``, ``capacity``, and ``subject_focus``.
    level : str
        The class level label, e.g. ``"standard"``, ``"honors"``, or
        ``"AP"``.
    assignment_lookup : dict[str, list[dict[str, Any]]]
        Mapping from class ID to the list of assignment dictionaries for
        that class.  Each assignment dict must contain a
        ``"student_name"`` key.

    Returns
    -------
    str
        HTML-formatted hover text string suitable for use as a Plotly
        ``text`` value.
    """
    capacity = cls.get("capacity", 30)
    enrolled = len(assignment_lookup.get(cls["id"], []))
    hover_text = f"Class: {cls.get('name', cls['id'])}<br>"
    hover_text += f"Level: {level}<br>"
    hover_text += f"Focus: {cls.get('subject_focus', 'N/A')}<br>"
    hover_text += f"Enrolled: {enrolled}/{capacity}"

    if cls["id"] in assignment_lookup:
        names = [a["student_name"] for a in assignment_lookup[cls["id"]]]
        hover_text += "<br><br>Students:<br>" + "<br>".join(names[:10])
        if len(names) > 10:
            hover_text += f"<br>...and {len(names) - 10} more"
    else:
        hover_text += "<br><br>No students assigned"

    return hover_text


def create_class_layout_visualization(
    classes: list[dict[str, Any]],
    assignments: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Create a visual representation of the school layout.

    Shows classes grouped by level, coloured by subject focus, and
    annotated with current enrollment information.

    Parameters
    ----------
    classes : list[dict[str, Any]]
        List of class dictionaries.  Each dict may contain the keys
        ``id``, ``name``, ``level``, ``subject_focus``, and ``capacity``.
    assignments : list[dict[str, Any]]
        List of assignment dictionaries.  Each dict must contain
        ``class_id`` and ``student_name``.

    Returns
    -------
    dict[str, Any]
        Plotly figure dictionary with ``"data"`` (list of trace dicts)
        and ``"layout"`` (layout dict) keys.
    """
    # Group classes by level
    levels = {}
    for cls in classes:
        level = cls.get("level", "standard")
        if level not in levels:
            levels[level] = []
        levels[level].append(cls)

    # Create assignment lookup (class_id -> list of assignments)
    assignment_lookup = {}
    for assign in assignments:
        cid = assign["class_id"]
        if cid not in assignment_lookup:
            assignment_lookup[cid] = []
        assignment_lookup[cid].append(assign)

    # Prepare data for scatter plot showing class layout
    traces = []

    # Color mapping for different subject focuses
    focus_colors = {
        "STEM": "#1f77b4",  # Blue
        "arts": "#ff7f0e",  # Orange
        "humanities": "#2ca02c",  # Green
    }

    # Level symbols
    level_symbols = {"standard": "circle", "honors": "square", "AP": "diamond"}

    level_order = ["standard", "honors", "AP"]
    for y_pos, level in enumerate(level_order):
        if level not in levels:
            continue
        level_classes = levels[level]

        x_positions = []
        y_positions = []
        colors = []
        symbols = []
        hover_texts = []

        for idx, cls in enumerate(sorted(level_classes, key=lambda c: c["id"])):
            x_positions.append(idx + 1)
            y_positions.append(y_pos + 1)

            colors.append(focus_colors.get(cls.get("subject_focus", ""), "#888888"))
            symbols.append(level_symbols.get(level, "circle"))
            hover_texts.append(_build_hover_text(cls, level, assignment_lookup))

        traces.append(
            {
                "type": "scatter",
                "x": x_positions,
                "y": y_positions,
                "mode": "markers",
                "marker": {
                    "size": 20,
                    "color": colors,
                    "symbol": symbols,
                    "line": {"width": 2, "color": "#000000"},
                },
                "text": hover_texts,
                "hoverinfo": "text",
                "name": f"{level.title()} Level",
                "showlegend": False,
            }
        )

    # Add legend traces for subject focuses
    for focus, color in focus_colors.items():
        traces.append(
            {
                "type": "scatter",
                "x": [None],
                "y": [None],
                "mode": "markers",
                "marker": {"size": 15, "color": color, "symbol": "circle"},
                "name": f"{focus} Focus",
                "legendgroup": "focus",
                "legendgrouptitle": {"text": "Subject Focus"},
            }
        )

    # Add legend traces for class levels
    for level, symbol in level_symbols.items():
        traces.append(
            {
                "type": "scatter",
                "x": [None],
                "y": [None],
                "mode": "markers",
                "marker": {
                    "size": 15,
                    "color": "#888888",
                    "symbol": symbol,
                    "line": {"width": 2, "color": "#000000"},
                },
                "name": f"{level.title()}",
                "legendgroup": "levels",
                "legendgrouptitle": {"text": "Class Levels"},
            }
        )

    layout = {
        "title": {"text": "School Class Layout & Assignments", "x": 0.5},
        "xaxis": {
            "title": "Class Position within Level",
            "showgrid": True,
            "zeroline": False,
            "dtick": 1,
        },
        "yaxis": {
            "title": "Class Level",
            "showgrid": True,
            "zeroline": False,
            "dtick": 1,
            "tickmode": "array",
            "tickvals": [1, 2, 3],
            "ticktext": ["Standard", "Honors", "AP"],
        },
        "hovermode": "closest",
        "showlegend": True,
        "legend": {
            "x": 1.02,
            "y": 1,
            "bgcolor": "rgba(255,255,255,0.8)",
            "bordercolor": "#000000",
            "borderwidth": 1,
        },
    }

    return {"data": traces, "layout": layout}


def create_class_enrollment_chart(
    assignments: list[dict[str, Any]],
    classes: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Create a stacked bar chart showing enrollment count per class.

    Each bar is split into enrolled students and available seats,
    coloured by subject focus.  Classes are ordered by level then name.

    Parameters
    ----------
    assignments : list[dict[str, Any]]
        List of assignment dictionaries.  Each dict must contain
        ``class_id``.
    classes : list[dict[str, Any]]
        List of class dictionaries.  Each dict may contain ``id``,
        ``name``, ``level``, ``subject_focus``, and ``capacity``.

    Returns
    -------
    dict[str, Any]
        Plotly figure dictionary with ``"data"`` and ``"layout"`` keys.
        Returns a figure with an empty data list when ``assignments`` is
        empty.
    """
    if not assignments:
        return {"data": [], "layout": {"title": "No assignments to display"}}

    # Count enrollments per class
    enrollment_counts = {}
    for assign in assignments:
        cid = assign["class_id"]
        enrollment_counts[cid] = enrollment_counts.get(cid, 0) + 1

    # Sort classes by level then name
    level_order = {"standard": 0, "honors": 1, "AP": 2}
    sorted_classes = sorted(
        classes, key=lambda c: (level_order.get(c.get("level", "standard"), 0), c.get("name", c["id"]))
    )

    class_names = [c.get("name", c["id"]) for c in sorted_classes]
    enrolled = [enrollment_counts.get(c["id"], 0) for c in sorted_classes]
    capacities = [c.get("capacity", 30) for c in sorted_classes]
    available = [cap - enr for cap, enr in zip(capacities, enrolled, strict=False)]

    focus_colors_map = {"STEM": "#1f77b4", "arts": "#ff7f0e", "humanities": "#2ca02c"}
    bar_colors = [focus_colors_map.get(c.get("subject_focus", ""), "#888888") for c in sorted_classes]

    traces = [
        {
            "type": "bar",
            "x": class_names,
            "y": enrolled,
            "name": "Enrolled",
            "marker": {"color": bar_colors},
            "text": [str(e) for e in enrolled],
            "textposition": "auto",
        },
        {
            "type": "bar",
            "x": class_names,
            "y": available,
            "name": "Available Seats",
            "marker": {"color": "#d3d3d3"},
        },
    ]

    layout = {
        "title": {"text": "Class Enrollment vs Capacity", "x": 0.5},
        "xaxis": {"title": "Class", "tickangle": -30},
        "yaxis": {"title": "Number of Students"},
        "barmode": "stack",
        "showlegend": True,
        "legend": {"x": 1.02, "y": 1},
    }

    return {"data": traces, "layout": layout}


def create_preference_satisfaction_chart(
    assignments: list[dict[str, Any]],
    students: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Create a bar chart of subject-focus preference satisfaction rates.

    For each subject focus type (STEM, arts, humanities) the chart shows
    the percentage of expressed preferences that were satisfied by the
    solver.

    Parameters
    ----------
    assignments : list[dict[str, Any]]
        List of assignment dictionaries.  Each dict may contain
        ``student_id``, ``focus_preference_match``, and
        ``subject_focus``.
    students : list[dict[str, Any]]
        List of student dictionaries.  Each dict may contain ``id`` and
        ``preferences`` (a list of subject-focus strings).

    Returns
    -------
    dict[str, Any]
        Plotly figure dictionary with ``"data"`` and ``"layout"`` keys.
        Returns a figure with an empty data list when ``assignments`` is
        empty.
    """
    if not assignments:
        return {"data": [], "layout": {"title": "No assignments to analyze"}}

    student_lookup = {s["id"]: s for s in students}

    focus_types = ["STEM", "arts", "humanities"]
    satisfied_counts = dict.fromkeys(focus_types, 0)
    total_counts = dict.fromkeys(focus_types, 0)

    for assignment in assignments:
        student = student_lookup.get(assignment["student_id"], {})
        preferences = student.get("preferences", [])

        for pref in preferences:
            if pref in total_counts:
                total_counts[pref] += 1
                if assignment.get("focus_preference_match") and assignment.get("subject_focus") == pref:
                    satisfied_counts[pref] += 1

    traces = []

    focus_labels = []
    satisfaction_rates = []
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

    for _i, focus in enumerate(focus_types):
        if total_counts[focus] > 0:
            rate = (satisfied_counts[focus] / total_counts[focus]) * 100
        else:
            rate = 0
        focus_labels.append(f"{focus} Focus")
        satisfaction_rates.append(rate)

    traces.append(
        {
            "type": "bar",
            "x": focus_labels,
            "y": satisfaction_rates,
            "marker": {"color": colors},
            "text": [f"{rate:.1f}%" for rate in satisfaction_rates],
            "textposition": "auto",
            "name": "Satisfaction Rate",
        }
    )

    layout = {
        "title": {"text": "Subject Focus Preference Satisfaction by Type", "x": 0.5},
        "xaxis": {"title": "Subject Focus"},
        "yaxis": {"title": "Satisfaction Rate (%)", "range": [0, 100]},
        "showlegend": False,
    }

    return {"data": traces, "layout": layout}


def create_class_utilization_dashboard(
    assignments: list[dict[str, Any]],
    classes: list[dict[str, Any]],
    students: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Create a stacked bar chart of capacity utilization by class level.

    Aggregates total capacity and actual enrollment for each class level
    (``standard``, ``honors``, ``AP``) and visualises the split between
    enrolled students and remaining available seats.

    Parameters
    ----------
    assignments : list[dict[str, Any]]
        List of assignment dictionaries.  Each dict must contain
        ``class_id``.
    classes : list[dict[str, Any]]
        List of class dictionaries.  Each dict may contain ``id``,
        ``level``, and ``capacity``.
    students : list[dict[str, Any]]
        List of student dictionaries.  Not used directly in the current
        implementation; reserved for future per-student breakdowns.

    Returns
    -------
    dict[str, Any]
        Plotly figure dictionary with ``"data"`` and ``"layout"`` keys.
    """
    # Calculate utilization by class level
    level_capacity = {}
    level_used = {}

    class_lookup = {c["id"]: c for c in classes}

    for cls in classes:
        level = cls.get("level", "standard")
        if level not in level_capacity:
            level_capacity[level] = 0
            level_used[level] = 0
        level_capacity[level] += cls.get("capacity", 30)

    # Calculate actual usage (each student = 1 seat)
    for assignment in assignments:
        cls = class_lookup.get(assignment["class_id"], {})
        level = cls.get("level")
        if level:
            level_used[level] += 1

    traces = []

    levels = list(level_capacity.keys())
    capacity_values = [level_capacity[lv] for lv in levels]
    used_values = [level_used[lv] for lv in levels]

    traces.append(
        {
            "type": "bar",
            "x": levels,
            "y": used_values,
            "name": "Enrolled Students",
            "marker": {"color": "#2ca02c"},
        }
    )

    traces.append(
        {
            "type": "bar",
            "x": levels,
            "y": [cap - used for cap, used in zip(capacity_values, used_values, strict=False)],
            "name": "Available Seats",
            "marker": {"color": "#d3d3d3"},
        }
    )

    layout = {
        "title": {"text": "Class Capacity Utilization by Level", "x": 0.5},
        "xaxis": {"title": "Class Level"},
        "yaxis": {"title": "Number of Students"},
        "barmode": "stack",
        "showlegend": True,
        "legend": {"x": 1.02, "y": 1},
    }

    return {"data": traces, "layout": layout}


def create_extended_day_chart(
    assignments: list[dict[str, Any]],
    metrics: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Create a bar chart comparing extended-day requests to outcomes.

    Shows three bars: total requests, granted, and denied, derived
    directly from the assignment data.

    Parameters
    ----------
    assignments : list[dict[str, Any]]
        List of assignment dictionaries.  Each dict may contain
        ``extended_day_requested`` and ``extended_day_granted``.
    metrics : dict[str, Any] or None
        Solution-level metrics dictionary.  Reserved for future use;
        not referenced in the current implementation.

    Returns
    -------
    dict[str, Any]
        Plotly figure dictionary with ``"data"`` and ``"layout"`` keys.
        Returns a figure with an empty data list when ``assignments`` is
        empty.
    """
    if not assignments:
        return {"data": [], "layout": {"title": "No assignments to display"}}

    requested = sum(1 for a in assignments if a.get("extended_day_requested") is not None)
    granted = sum(1 for a in assignments if a.get("extended_day_granted"))
    denied = requested - granted

    traces = [
        {
            "type": "bar",
            "x": ["Requested", "Granted", "Denied"],
            "y": [requested, granted, denied],
            "marker": {"color": ["#1f77b4", "#2ca02c", "#d62728"]},
            "text": [str(requested), str(granted), str(denied)],
            "textposition": "auto",
        }
    ]

    layout = {
        "title": {"text": "Extended Day Requests", "x": 0.5},
        "xaxis": {"title": "Status"},
        "yaxis": {"title": "Number of Students"},
        "showlegend": False,
    }

    return {"data": traces, "layout": layout}


def create_assignment_summary_pie(assignments: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Create a pie chart of overall subject-preference satisfaction.

    Splits all assignments into two segments: those where the student's
    subject-focus preference was satisfied and those where it was not.

    Parameters
    ----------
    assignments : list[dict[str, Any]]
        List of assignment dictionaries.  Each dict may contain a
        boolean ``focus_preference_match`` field.

    Returns
    -------
    dict[str, Any]
        Plotly figure dictionary with ``"data"`` and ``"layout"`` keys.
        Returns a figure with an empty data list when ``assignments`` is
        empty.
    """
    if not assignments:
        return {"data": [], "layout": {"title": "No assignments to display"}}

    satisfied = sum(1 for a in assignments if a.get("focus_preference_match"))
    not_satisfied = len(assignments) - satisfied

    traces = [
        {
            "type": "pie",
            "labels": ["Preferences Satisfied", "Preferences Not Satisfied"],
            "values": [satisfied, not_satisfied],
            "marker": {"colors": ["#2ca02c", "#ff7f0e"]},
            "textinfo": "label+percent+value",
            "hovertemplate": "<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>",
        }
    ]

    layout = {
        "title": {"text": "Overall Student Subject Preference Satisfaction", "x": 0.5},
        "showlegend": True,
    }

    return {"data": traces, "layout": layout}


def generate_visual_assets(
    input_data: dict[str, Any],
    solution: dict[str, Any],
    statistics: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Generate all visual assets for the class assignment problem.

    Builds a complete set of Nextmv-compatible Plotly visualizations
    covering class layout, enrollment, preference satisfaction, capacity
    utilization, assignment summary, and extended-day requests.

    Parameters
    ----------
    input_data : dict[str, Any]
        Raw problem input.  Expected to contain ``"students"`` and
        ``"classes"`` lists.
    solution : dict[str, Any]
        Solver output.  Expected to contain an ``"assignments"`` list
        where each entry has at minimum ``class_id``, ``student_id``,
        and ``student_name``.
    statistics : dict[str, Any]
        Solver statistics passed through to individual chart generators.

    Returns
    -------
    list[dict[str, Any]]
        List of visual-asset dictionaries, each containing ``"name"``,
        ``"content_type"``, ``"visual"``, and ``"content"`` keys
        compatible with the Nextmv platform.
    """
    students = input_data.get("students", [])
    classes = input_data.get("classes", [])
    assignments = solution.get("assignments", [])

    # Generate all visualizations
    class_layout = create_class_layout_visualization(classes, assignments)
    enrollment_chart = create_class_enrollment_chart(assignments, classes)
    preference_chart = create_preference_satisfaction_chart(assignments, students)
    utilization_dashboard = create_class_utilization_dashboard(assignments, classes, students)
    summary_pie = create_assignment_summary_pie(assignments)
    extended_day_chart = create_extended_day_chart(assignments, statistics)

    visual_assets = [
        {
            "name": "Class Layout",
            "content_type": "json",
            "visual": {
                "schema": "plotly",
                "type": "custom-tab",
                "label": "Class Layout",
            },
            "content": [class_layout],
        },
        {
            "name": "Enrollment",
            "content_type": "json",
            "visual": {"schema": "plotly", "type": "custom-tab", "label": "Enrollment"},
            "content": [enrollment_chart],
        },
        {
            "name": "Preference Satisfaction",
            "content_type": "json",
            "visual": {
                "schema": "plotly",
                "type": "custom-tab",
                "label": "Preferences",
            },
            "content": [preference_chart],
        },
        {
            "name": "Class Utilization",
            "content_type": "json",
            "visual": {
                "schema": "plotly",
                "type": "custom-tab",
                "label": "Utilization",
            },
            "content": [utilization_dashboard],
        },
        {
            "name": "Assignment Summary",
            "content_type": "json",
            "visual": {"schema": "plotly", "type": "custom-tab", "label": "Summary"},
            "content": [summary_pie],
        },
        {
            "name": "Extended Day",
            "content_type": "json",
            "visual": {"schema": "plotly", "type": "custom-tab", "label": "Extended Day"},
            "content": [extended_day_chart],
        },
    ]

    return visual_assets
