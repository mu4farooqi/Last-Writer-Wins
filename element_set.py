"""
Implementation of Last-Writer-Wins (LWW) Element Set using ZSET(Redis) in Python
"""

import redis
import string
import logging
from random import choice
from dateutil.parser import parse
from datetime import datetime


class ZSet(dict):
    """
    ZSet class acts same like python dictionary(dict). Only difference is that in ZSet class our data is stored in
    Redis' ZSET structure
    """
    def __init__(self, redis_instance):
        """
        This method will initialize ZSet class using given redis_instance and will create a unique key for ZSET
        :param redis_instance: Instance of StrictRedis
        :return: ZSet object
        :rtype: ZSet
        """
        super(ZSet, self).__init__()
        self.redis_instance = redis_instance
        self.set_key = ''.join([choice(string.ascii_letters + string.digits) for n in xrange(5)])

    def __setitem__(self, element, timestamp):
        """
        This method is equivalent to `self[element] = timestamp`
        :param str element: Value of Element
        :param datetime timestamp: DateTime string of Timestamp
        :return:
        """
        assert isinstance(timestamp, datetime)
        assert isinstance(element, basestring)

        # Total number of seconds relative to epoch time
        total_number_of_seconds = (timestamp - datetime(1970, 1, 1)).total_seconds()
        self.redis_instance.zadd(self.set_key, total_number_of_seconds, element)

    def __getitem__(self, element):
        """
        This method is equivalent to `self[element]`
        :param str element: Value of Element
        :return: Timestamp of Element
        :rtype: datetime
        """
        timestamp = self.redis_instance.zscore(self.set_key, element)
        return datetime.fromtimestamp(timestamp) if timestamp else None

    def __contains__(self, element):
        """
        This method is equivalent to `element in self`
        :param str element: Value of Element
        :return: True|False
        :rtype: bool
        """
        return True if self[element] else False

    def keys(self):
        """
        This method will return all elements in ZSet
        :return: List of elements in ZSet
        :rtype: list
        """
        return self.redis_instance.zrange(self.set_key, 0, -1)


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
        This method will initialize a last writer wins element set. We are using redis sorted set i.e. ZSet()
        for our implementation
        :return: Instance of LastWriterWinsSet object
        :rtype: LastWriterWinsSet
        """
        redis_instance = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.add_set = ZSet(redis_instance)
        self.remove_set = ZSet(redis_instance)

    def add(self, element, timestamp=datetime.utcnow().isoformat()):
        """
        This method will add/modify an element in add_set according to following two conditions:

            --> If element already exists in add_set and stored timestamp is older than the given timestamp then
             current timestamp of the stored element will be updated otherwise nothing should be done.
            --> If element doesn't exits in add_set then we'll simply add element to the add_set with its
                timestamp.

        :param str element: Value of element which is to be added in add_set
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

        :param str element: Value of element which is to be added in remove_set
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

    def exists(self, element):
        """
        This method will determine either given element is in Element set or not according to following conditions:

            --> If element is present in add_set but not in remove_set then return True
            --> If element is not present in add_set then return False
            --> If element is present in both add_set and remove_set and timestamp of add_set is more recent then True

            Note: I'm assuming timestamps of an element in add_set and remove_set couldn't be same but if they are same
            this method will still return False as timestamp of element in add_set is not more recent
        :param str element: Value of element
        :return: Boolean variable indicating either element is present or not
        :rtype: bool
        """
        if element in self.add_set and (element
                                        not in self.remove_set or self.add_set[element] > self.remove_set[element]):
            return True
        return False

    def get(self):
        """
        This method will return all elements in element set. An element will be in return list if:

            --> If element is present in add_set but not in remove_set
            --> If element is present in both add_set and remove_set and timestamp of add_set is more recent
        :return: List of all elements in Element Set
        :rtype: list
        """
        elements_of_add_set_not_in_remove_set = list(set(self.add_set.keys()) - set(self.remove_set.keys()))
        common_elements_of_add_and_remove_set = list(set(self.add_set.keys()).intersection(set(self.remove_set.keys())))
        return elements_of_add_set_not_in_remove_set + filter(
                lambda element: self.add_set[element] > self.remove_set[element], common_elements_of_add_and_remove_set)