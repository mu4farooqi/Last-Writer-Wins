"""
Implementation of Last-Writer-Wins (LWW) Element Set using dict(HashTable) in Python
"""

import logging
from dateutil.parser import parse
from datetime import datetime


class LastWriterWinsSet(object):
    """
    Last-Writer-Wins (LWW) Element Set is a common data structure used to implement conflict-free replicated
    data type (CRDT). This set stores only one instance of each element in the set, and associates it with a
    timestamp. The operations on the LWW Element Set are:

        --> LastWriterWinsSet()
        --> add()
        --> remove()
        --> exists()
        --> get()

    """
    def __init__(self):
        """
        This method will initialize a last writer wins element set. We are using dict() for our implementation
        which is implementation of Hashtable for Python. Access time for dict(Hashtable) is certainly constant
        i.e. O(1)
        :return: Instance of LastWriterWinsSet object
        :rtype: LastWriterWinsSet
        """
        self.add_set = dict()
        self.remove_set = dict()

    def add(self, element, timestamp=datetime.utcnow().isoformat()):
        """
        This method will add/modify an element in add_set according to following two conditions:

            --> If element already exists in add_set and stored timestamp is older than the given timestamp then
             current timestamp of the stored element will be updated otherwise nothing should be done.
            --> If element doesn't exits in add_set then we'll simply add element to the add_set with its
                timestamp.

        :param object element: Value of element which is to be added in add_set
        :param str timestamp: DateTime string of Timestamp (Preferably in isoformat but not necessary).
        If nothing is provided then current utc datetime value would be used
        :return: None
        :rtype:
        """
        assert element, "Value of element cannot be None"
        assert timestamp, "Value of timestamp cannot be None"

        try:
            timestamp = parse(timestamp)
        except ValueError as exception:
            logging.error('Unable to parse time stamps %s because of an exception: %s', timestamp, exception.message)
            return

        if element not in self.add_set or self.add_set[element] < timestamp:
            self.add_set[element] = timestamp

    # TODO: add and remove methods can be combined in a single method with an extra flag indicating add/remove operation
    def remove(self, element, timestamp=datetime.utcnow().isoformat()):
        """
        This method will add/modify an element in remove_set according to following two conditions:

            --> If element already exists in remove_set and stored timestamp is older than the given timestamp
                then current timestamp of the stored element will be updated otherwise nothing should be done.
            --> If element doesn't exits in remove_set then we'll simply add element to the remove_set with its
                timestamp.

        :param object element: Value of element which is to be added in remove_set
        :param str timestamp: DateTime string of Timestamp (Preferably in isoformat but not necessary).
        If nothing is provided then current utc datetime value would be used
        :return: None
        :rtype:
        """
        assert element, "Value of element cannot be None"
        assert timestamp, "Value of timestamp cannot be None"

        try:
            timestamp = parse(timestamp)
        except ValueError as exception:
            logging.error('Unable to parse time stamps %s because of an exception: %s', timestamp, exception.message)
            return

        if element not in self.remove_set or self.remove_set[element] < timestamp:
            self.remove_set[element] = timestamp
