/*
 Copyright (C) 2019 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

let viewModel = can.Map.extend({
  define: {
    trigger: {
      type: 'boolean',
      set: function (value) {
        if (!this.attr('activated') && value) {
          this.attr('activated', true);
        }
      },
    },
  },
  activated: false,
});

/**
 *
 */
export default can.Component.extend({
  tag: 'lazy-render',
  template: can.stache('{{#if activated}}<content/>{{/if}}'),
  leakScope: true,
  viewModel,
});
