/*
 Copyright (C) 2019 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import template from './date-form-field-view.stache';

export default can.Component.extend({
  tag: 'date-form-field-view',
  template: can.stache(template),
  leakScope: true,
  viewModel: {
    value: null,
    disabled: false,
  },
});
