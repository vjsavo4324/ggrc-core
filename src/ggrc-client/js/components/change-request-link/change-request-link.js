/*
    Copyright (C) 2019 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import template from './templates/change-request-link.stache';

const viewModel = can.Map.extend({
  define: {
    link: {
      get() {
        return GGRC.config.CHANGE_REQUEST_URL;
      },
    },
  },
});

export default can.Component.extend({
  tag: 'change-request-link',
  template: can.stache(template),
  leakScope: true,
  viewModel,
});
