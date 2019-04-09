/*
 Copyright (C) 2019 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import '../../numberbox/numberbox';
import template from './templates/numberbox-form-field.stache';
import {TEXT_FORM_FIELD_VM} from './text-form-field';

export default can.Component.extend({
  tag: 'numberbox-form-field',
  template: can.stache(template),
  leakScope: true,
  viewModel: TEXT_FORM_FIELD_VM,
  events: {
    inserted() {
      this.viewModel.attr('textField', this.element.find('.text-field'));
    },
  },
});
