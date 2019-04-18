# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Unit tests for retry decorator."""

import unittest

from ggrc.utils import retry


class TestRetry(unittest.TestCase):
  """Test case for retry decorator."""

  def __init__(self, *args, **kwargs):
    super(TestRetry, self).__init__(*args, **kwargs)
    self.counter = 0

  def test_retry_with_errors(self):
    """Tests retry decorator when function generate exception."""
    self.counter = 0

    @retry(Exception, delay=0.1)
    def test_function():
      """Test function."""
      while self.counter < 3:
        self.counter += 1
        raise Exception()
      return 0

    result = test_function()
    self.assertEquals(result, 0)
    self.assertEquals(self.counter, 3)

  def test_retry_no_errors(self):
    """Tests function without exception."""
    self.counter = 0

    @retry(Exception, delay=0.1)
    def test_function():
      """Test function."""
      self.counter += 1
      return 0

    result = test_function()
    self.assertEquals(result, 0)
    self.assertEquals(self.counter, 1)

  def test_retry_with_always_errors(self):
    """Tests retry decorator for failing function."""
    self.counter = 0

    @retry(Exception, tries=1, delay=0.1)
    def test_function():
      """Test function."""
      self.counter += 1
      raise Exception()

    with self.assertRaises(Exception):
      test_function()
    self.assertEquals(self.counter, 2)
