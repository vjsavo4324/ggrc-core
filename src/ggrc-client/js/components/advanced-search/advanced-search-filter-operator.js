/*
 Copyright (C) 2019 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import template from './advanced-search-filter-operator.stache';

/**
 * Filter Operator view model.
 * Contains logic used in Filter Operator component
 * @constructor
 */
let viewModel = can.Map.extend({
  /**
   * Contains operation name.
   * @type {string}
   * @example
   * AND
   * OR
   */
  operator: '',
});

/**
 * Filter Operator is a component representing operation connecting Advanced Search items.
 */
export default can.Component.extend({
  tag: 'advanced-search-filter-operator',
  template: can.stache(template),
  leakScope: true,
  viewModel: viewModel,
});
