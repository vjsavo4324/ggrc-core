# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Decorators."""
# pylint: disable=protected-access

import logging
import time
from functools import wraps

from lib import constants, environment, exception, file_ops, users
from lib.utils import selenium_utils

LOGGER = logging.getLogger(__name__)


def take_screenshot_on_error(fun):
  """Decorate method and make screenshot on any exception."""
  # todo: replace with pytest-selenium which automagically takes
  def wrapper(self, *args):
    "Wrapper."
    try:
      return fun(self, *args)
    except Exception as exc:
      LOGGER.error(exc)
      file_path = (environment.LOG_PATH + self.__class__.__name__ + "." +
                   self._driver.title)
      unique_file_path = file_ops.get_unique_postfix(file_path, ".png")
      self._driver.get_screenshot_as_file(unique_file_path)
      raise
  return wrapper


def wait_for_redirect(fun):
  """Decorates methods and wait until URL has changed."""
  @wraps(fun)
  def wrapper(self, *args, **kwargs):
    "Wrapper."
    from_url = self._driver.current_url
    result = fun(self, *args, **kwargs)
    timer_start = time.time()
    while from_url == self._driver.current_url:
      time.sleep(0.1)
      if time.time() - timer_start > constants.ux.MAX_USER_WAIT_SECONDS:
        raise exception.RedirectTimeout(
            "Failed to redirect from {} to {}".format(
                from_url, self._driver.current_url))
    return result
  return wrapper


def handle_alert(fun):
  """Accept or dismiss alert."""
  @wraps(fun)
  def wrapper(self, *args, **kwargs):
    "Wrapper."
    result = fun(self, *args, **kwargs)
    selenium_utils.handle_alert(self._driver, accept=True)
    return result
  return wrapper


def lazy_property(fun):
  """Decorator for lazy initialization of property."""
  prop_name = "_lazy_" + fun.__name__

  @property
  def lazy(self):
    """Check if property exist in object, if no setattr"""
    if not hasattr(self, prop_name):
      setattr(self, prop_name, fun(self))
    return getattr(self, prop_name)
  return lazy


def memoize(func):
  """Decorator for memoization of function results"""
  cache = func.cache = {}

  @wraps(func)
  def memoizer(*args, **kwargs):
    """Call a function and put its result into the cache"""
    key = str(args) + str(kwargs)
    if key not in cache:
      cache[key] = func(*args, **kwargs)
    return cache[key]
  return memoizer


def track_time(fun):
  """Time tracking decorator which defines how long 'fun' was executing."""
  @wraps(fun)
  def wrapper(*args, **kwargs):
    "Wrapper."
    start_time = time.time()
    result = fun(*args, **kwargs)
    elapsed_time = time.time() - start_time
    print "Execution of '{0:s}' function took {1:.3f} s".format(
        fun.func_name, elapsed_time)
    return result
  return wrapper


def work_by_external_user(fun):
  """Decorator to work by external user and return to previous user."""
  from lib.entities import entities_factory

  def wrapper(*args, **kwargs):
    "Wrapper."
    user = users.current_user()
    users.set_current_user(users.EXTERNAL_APP_USER)
    users.set_current_user(entities_factory.PeopleFactory.external_app_user)
    result = fun(*args, **kwargs)
    users.set_current_user(user)
    return result
  return wrapper


def check_that_obj_is_created(fun):
  """Decorator to check if object is created."""
  def wrapper(*args, **kwargs):
    "Wrapper."
    from lib.service import rest_service
    result = fun(*args, **kwargs)
    # need to wait when creation background job is finished
    rest_service.ObjectsInfoService().get_obj(result)
    return result
  return wrapper
