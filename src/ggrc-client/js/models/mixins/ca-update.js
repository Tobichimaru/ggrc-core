/*
    Copyright (C) 2019 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import Mixin from './mixin';

export default Mixin.extend({}, {
  after_save: function () {
    this.dispatch('readyForRender');
  },
  info_pane_preload: function () {
    this.refresh();
  },
});
