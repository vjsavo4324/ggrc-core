/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import template from './templates/tree-filter-input.mustache';

(function (can, GGRC) {
  'use strict';

  let viewModel = can.Map.extend({
    define: {
      filter: {
        type: 'string',
        set: function (newValue) {
          this.attr('options.filter', newValue || '');
          this.onFilterChange(newValue);
          return newValue;
        },
      },
      operation: {
        type: 'string',
        value: 'AND',
      },
      depth: {
        type: 'boolean',
        value: false,
      },
      isExpression: {
        type: 'boolean',
        value: false,
      },
      filterDeepLimit: {
        type: 'number',
        value: 0,
      },
    },
    disabled: false,
    showAdvanced: false,
    options: {},
    filters: null,
    init: function () {
      let options = this.attr('options');
      let filter = this.attr('filter');
      let operation = this.attr('operation');
      let depth = this.attr('depth');
      let filterDeepLimit = this.attr('filterDeepLimit');

      options.attr('filter', filter);
      options.attr('operation', operation);
      options.attr('depth', depth);
      options.attr('filterDeepLimit', filterDeepLimit);
      options.attr('name', 'custom');

      if (this.registerFilter) {
        this.registerFilter(options);
      }
    },
    submit: function () {
      this.dispatch('submit');
    },
    onFilterChange: function (newValue) {
      let filter = GGRC.query_parser.parse(newValue);
      let isExpression =
        !!filter && !!filter.expression.op &&
        filter.expression.op.name !== 'text_search' &&
        filter.expression.op.name !== 'exclude_text_search';
      this.attr('isExpression', isExpression);
    },
    openAdvancedFilter: function () {
      this.dispatch('openAdvanced');
    },
    removeAdvancedFilters: function () {
      this.dispatch('removeAdvanced');
    },
  });

  GGRC.Components('treeFilterInput', {
    tag: 'tree-filter-input',
    template: template,
    viewModel: viewModel,
    events: {
      'input keyup': function (el, ev) {
        this.viewModel.onFilterChange(el.val());

        if (ev.keyCode === 13) {
          this.viewModel.submit();
        }
        ev.stopPropagation();
      },
      '{viewModel} disabled': function () {
        this.viewModel.attr('filter', '');
      },
    },
  });
})(window.can, window.GGRC);
