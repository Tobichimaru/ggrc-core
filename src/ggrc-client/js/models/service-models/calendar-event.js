/*
    Copyright (C) 2018 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import Cacheable from '../cacheable';

export default Cacheable('CMS.Models.CalendarEvent', {
  root_object: 'calendar_event',
  root_collection: 'calendar_events',
  findAll: 'GET /api/calendar_events',
}, {});
