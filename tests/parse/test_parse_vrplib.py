import numpy as np
import pytest
from numpy.testing import assert_equal

from vrplib.parse.parse_vrplib import (
    group_specifications_and_sections,
    parse_section,
    parse_specification,
    parse_vrplib,
)


def test_group_specifications_and_sections():
    """
    Check if instance lines are correctly grouped into specifications
    and sections.
    """
    specs = [
        "NAME : ORTEC-VRPTW-ASYM-00c5356f-d1-n258-k12",
        "COMMENT : ORTEC",
    ]
    sections = [
        "EDGE_WEIGHT_SECTION",
        "0	1908",
        "1994	0",
        "TIME_WINDOW_SECTION",
        "1	0	41340",
        "2	15600	23100",
    ]

    lines = specs + sections + ["EOF"]
    actual_specs, actual_sections = group_specifications_and_sections(lines)

    assert_equal(actual_specs, specs)
    assert_equal(actual_sections, [sections[:3], sections[3:]])


@pytest.mark.parametrize(
    "line, key, value",
    [
        ("NAME : Antwerp 1", "name", "Antwerp 1"),  # Whitespace around :
        ("COMMENT:'test' ", "comment", "'test'"),  # No whitespace around :
        ("COMMENT: BKS:1", "comment", "BKS:1"),  # Split at first :
        ("CAPACITY: 30", "capacity", 30),  # int value
        ("CAPACITY: 30.5", "capacity", 30.5),  # float value
        ("name: Antwerp 1", "name", "Antwerp 1"),  # OK if key is not uppercase
    ],
)
def test_parse_specification(line, key, value):
    """
    Tests if a specification line is correctly parsed.
    """
    k, v = parse_specification(line)

    assert_equal(k, key)
    assert_equal(v, value)


@pytest.mark.parametrize(
    "lines, desired",
    [
        (
            ["SERVICE_TIME_SECTION", "1  2", "2  3", "3  100"],
            ["service_time", np.array([2, 3, 100])],
        ),
        (
            ["TIME_WINDOW_SECTION", "1  2  3", "2  1  2"],
            ["time_window", np.array([[2, 3], [1, 2]])],
        ),
        (
            ["DEMAND_SECTION", "1  1.1", "2  2.2", "3  3.3"],
            ["demand", np.array([1.1, 2.2, 3.3])],
        ),
        (
            ["DEPOT_SECTION", "1", "-1"],
            ["depot", np.array([0])],
        ),
        (
            ["UNKNOWN_SECTION", "1 1", "1 -1"],
            ["unknown", np.array([1, -1])],
        ),
    ],
)
def test_parse_section(lines, desired):
    """
    Tests if data sections (excluding edge weights) are parsed correctly.
    """
    actual = parse_section(lines, {})

    assert_equal(actual, desired)


def test_parse_vrplib():
    instance = "\n".join(
        [
            "NAME: VRPLIB",
            "EDGE_WEIGHT_TYPE: EXPLICIT",
            "EDGE_WEIGHT_FORMAT: FULL_MATRIX",
            "EDGE_WEIGHT_SECTION",
            "0  1",
            "1  0",
            "SERVICE_TIME_SECTION",
            "1  1",
            "TIME_WINDOW_SECTION",
            "1  1   2",
            "EOF",
        ]
    )
    actual = parse_vrplib(instance)

    desired = dict(
        name="VRPLIB",
        edge_weight_type="EXPLICIT",
        edge_weight_format="FULL_MATRIX",
        edge_weight=np.array([[0, 1], [1, 0]]),
        service_time=np.array([1]),
        time_window=np.array([[1, 2]]),
    )

    assert_equal(actual, desired)


def test_empty_text():
    """
    Tests if an empty text file is still read correctly.
    """
    actual = parse_vrplib("")
    assert_equal(actual, {})
