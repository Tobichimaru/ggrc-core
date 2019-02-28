# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Module with tools to move from html to markdown."""

from HTMLParser import HTMLParser


class HTML2MarkdownParser(HTMLParser):
  """HTMLParser for moving html text to markdown.

    1) Will replace html links <a href="..."> with markdown links (...)[...]
    2) Will replace <li> with dash sign "-" and </li> as newline sign "\n"
    3) Will remove other html tags (<strong>, <i> and others).

    self.fed - is a cleaned data without html tags.
  """

  def __init__(self):
    """Initialize parser."""
    HTMLParser.__init__(self)
    self.reset()
    self.fed = []
    self.last_tag = None
    self.current_link = None

  def get_data(self):
    """Get data after parsing."""
    return u''.join(self.fed)

  def handle_endtag(self, tag):
    """Handle ending html tag"""
    lower_tag = tag.lower()
    if lower_tag == 'li':
      self.fed.append('\n')

  def handle_starttag(self, tag, attrs):
    """Handle starting html tag."""
    lower_tag = tag.lower()
    self.last_tag = lower_tag
    attrs_dict = {key: value for key, value in attrs}
    if lower_tag == 'a':
      href = attrs_dict.get('href', '')
      self.current_link = "(" + href + ")" if href else ''
    elif lower_tag == 'li':
      self.fed.append('- ')
    elif lower_tag == 'img':
      src = attrs_dict.get('src', '')
      self.fed.append(src)

  def handle_data(self, data):
    """Handle data inside or outside tags."""
    if self.last_tag == 'a':
      self.fed.append("[" + data + "]" if data.strip() else '[link]')
      self.fed.append(self.current_link)
    else:
      self.fed.append(data)
