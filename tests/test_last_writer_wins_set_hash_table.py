"""
This module will test HashTable implementation of Last-Writer-Wins (LWW) Element Set using pytest
"""

import string
import pytest
from random import choice
from datetime import datetime, timedelta
from element_set import LastWriterWinsSet

ELEMENT = ''.join([choice(string.ascii_letters + string.digits) for n in xrange(5)])


@pytest.fixture()
def lww_set_object():
    """
    This fixture will create a LastWriterWinsSet object which will be shared by all tests in this module.
    :return:
    """
    set_object = LastWriterWinsSet()
    return set_object


def test_lww_set_initialize(lww_set_object):
    """
    This test will test initializer of LastWriterWinsSet
    """
    assert hasattr(lww_set_object, 'add_set') and isinstance(lww_set_object.add_set, dict)
    assert hasattr(lww_set_object, 'remove_set') and isinstance(lww_set_object.remove_set, dict)


def test_lww_set_add(lww_set_object):
    """
    This test will test add operation of LastWriterWinsSet
    """

    # Add a new element in set with incorrect timestamp
    lww_set_object.add(ELEMENT, 'TEMP')
    assert ELEMENT not in lww_set_object.add_set

    # Add a new element in set with default current utc timestamp
    lww_set_object.add(ELEMENT)
    assert isinstance(lww_set_object.add_set[ELEMENT], datetime)

    current_time_stamp_of_element = lww_set_object.add_set[ELEMENT]

    # Add an existing element in set with old time stamp
    lww_set_object.add(ELEMENT, (current_time_stamp_of_element - timedelta(days=1)).isoformat())
    assert isinstance(lww_set_object.add_set[ELEMENT], datetime)
    assert lww_set_object.add_set[ELEMENT] == current_time_stamp_of_element

    # Add an existing element in set with new time stamp
    lww_set_object.add(ELEMENT, (current_time_stamp_of_element + timedelta(days=1)).isoformat())
    assert isinstance(lww_set_object.add_set[ELEMENT], datetime)
    assert lww_set_object.add_set[ELEMENT] > current_time_stamp_of_element


def test_lww_set_remove(lww_set_object):
    """
    This test will test remove operation of LastWriterWinsSet
    """

    # Remove a new element from set with incorrect timestamp
    lww_set_object.remove(ELEMENT, 'TEMP')
    assert ELEMENT not in lww_set_object.remove_set

    # Remove a new element from set with default current utc timestamp
    lww_set_object.remove(ELEMENT)
    assert isinstance(lww_set_object.remove_set[ELEMENT], datetime)

    current_time_stamp_of_element = lww_set_object.remove_set[ELEMENT]

    # Remove an existing element from set with old time stamp
    lww_set_object.remove(ELEMENT, (current_time_stamp_of_element - timedelta(days=1)).isoformat())
    assert isinstance(lww_set_object.remove_set[ELEMENT], datetime)
    assert lww_set_object.remove_set[ELEMENT] == current_time_stamp_of_element

    # Remove an existing element from set with new time stamp
    lww_set_object.remove(ELEMENT, (current_time_stamp_of_element + timedelta(days=1)).isoformat())
    assert isinstance(lww_set_object.remove_set[ELEMENT], datetime)
    assert lww_set_object.remove_set[ELEMENT] > current_time_stamp_of_element


def test_lww_set_exists(lww_set_object):
    """
    This test will test either an element exists in Element set or not
    """

    # Add a new element in set with default current utc timestamp
    lww_set_object.add(ELEMENT)
    assert lww_set_object.exists(ELEMENT)

    # Remove an existing element from set with old utc timestamp
    lww_set_object.remove(ELEMENT, (datetime.utcnow() - timedelta(days=1)).isoformat())
    assert lww_set_object.exists(ELEMENT)

    # Remove an existing element from set default current utc timestamp
    lww_set_object.remove(ELEMENT)
    assert not lww_set_object.exists(ELEMENT)

    # If element doesn't exist at all in Element set
    assert not lww_set_object.exists(ELEMENT + 'TEMP')


def test_lww_set_get(lww_set_object):
    """
    This test will test either an element exists in Element set or not
    """

    # Add a new element in set with default current utc timestamp
    lww_set_object.add(ELEMENT)
    assert [ELEMENT] == lww_set_object.get()

    # Remove an existing element from set with old utc timestamp
    lww_set_object.remove(ELEMENT, (datetime.utcnow() - timedelta(days=1)).isoformat())
    assert [ELEMENT] == lww_set_object.get()

    # Remove an existing element from set default current utc timestamp
    lww_set_object.remove(ELEMENT)
    assert not lww_set_object.get()  # Is Empty ?



