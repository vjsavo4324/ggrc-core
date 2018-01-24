/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import template from './templates/mapper-results-items-header.mustache';

(function (can, GGRC, CMS) {
  'use strict';

  GGRC.Components('mapperResultsItemsHeader', {
    tag: 'mapper-results-items-header',
    template: template,
    viewModel: {
      columns: [],
      sortKey: '',
      sortDirection: 'asc',
      modelType: '',
      isSorted: function (attr) {
        return attr.attr('attr_sort_field') === this.attr('sortKey');
      },
      isSortedAsc: function () {
        return this.attr('sortDirection') === 'asc';
      },
      applySort: function (attr) {
        if (this.isSorted(attr)) {
          this.toggleSortDirection();
          return;
        }
        this.attr('sortKey', attr.attr('attr_sort_field'));
        this.attr('sortDirection', 'asc');
      },
      toggleSortDirection: function () {
        if (this.attr('sortDirection') === 'asc') {
          this.attr('sortDirection', 'desc');
        } else {
          this.attr('sortDirection', 'asc');
        }
      },
    },
  });
})(window.can, window.GGRC, window.CMS);
