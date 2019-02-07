/*
 Copyright (C) 2019 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import template from './templates/tree-item-status-for-workflow.stache';

const viewModel = can.Map.extend({
  define: {
    statusCSSClass: {
      type: 'string',
      get() {
        const status = this.attr('instance.status');
        let result = '';

        if (status) {
          const postfix = status
            .replace(/[\s\t]+/g, '')
            .toLowerCase();
          result = `state-${postfix}`;
        }

        return result;
      },
    },
  },
  instance: {},
});

export default can.Component.extend({
  tag: 'tree-item-status-for-workflow',
  template: can.stache(template),
  leakScope: true,
  viewModel,
});
