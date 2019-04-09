/*
 Copyright (C) 2019 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import '../simple-popover/simple-popover';
import {getAvailableAttributes} from '../../plugins/utils/tree-view-utils';
import * as AdvancedSearch from '../../plugins/utils/advanced-search-utils';
import template from './advanced-search-mapping-criteria.stache';
import Mappings from '../../models/mappers/mappings';
import * as businessModels from '../../models/business-models';

/**
 * Mapping Criteria view model.
 * Contains logic used in Mapping Criteria component.
 * @constructor
 */
let viewModel = can.Map.extend({
  define: {
    /**
     * Contains object represents criteria.
     * Contains the following fields: objectName, filter, mappedTo.
     * Initializes filter with Filter Attribute model.
     * @type {can.Map}
     */
    criteria: {
      type: '*',
      Value: can.Map,
      set: function (criteria) {
        if (!criteria.filter) {
          criteria.attr('filter',
            AdvancedSearch.create.attribute());
        }
        return criteria;
      },
    },
    /**
     * Indicates that criteria can be transformed to Mapping Group.
     * @type {boolean}
     */
    canBeGrouped: {
      type: 'boolean',
      value: false,
      get: function () {
        return this.attr('extendable') &&
         !(this.attr('criteria.mappedTo') && !this.attr('childCanBeGrouped'));
      },
    },
    /**
     * Indicates that child Mapping Criteria can be added.
     * @type {boolean}
     */
    canAddMapping: {
      type: 'boolean',
      value: false,
      get: function () {
        return !this.attr('criteria.mappedTo');
      },
    },
    /**
     * Indicates that popover should be displayed.
     * @type {boolean}
     */
    showPopover: {
      type: 'boolean',
      value: false,
      get: function () {
        return this.attr('canBeGrouped') && this.attr('canAddMapping');
      },
    },
  },
  /**
   * Indicates that child Mappping Criteria can be transformed to Mapping Group.
   * @type {boolean}
   */
  childCanBeGrouped: false,
  /**
   * Contains specific model name.
   * @type {string}
   * @example
   * Requirement
   * Regulation
   */
  modelName: null,
  /**
   * Indicates that Criteria is created on the root level.
   * Used for displaying correct label.
   */
  root: false,
  /**
   * Indicates that Criteria can be transformed to Mapping Group.
   * @type {boolean}
   */
  extendable: false,
  /**
   * Indicates that it is in assessment-template-clone-modal
   * @type {boolean}
   */
  isClone: false,
  /**
   * Returns a list of available attributes for specific model.
   * @return {can.List} - List of available attributes.
   */
  availableAttributes: function () {
    return getAvailableAttributes(this.attr('criteria.objectName'));
  },
  /**
   * Returns a list of available mapping types for specific model.
   * @return {Array} - List of available mapping types.
   */
  mappingTypes: function () {
    if (this.attr('isClone')) {
      let modelName = this.attr('modelName');

      this.attr('criteria.objectName', modelName);
      return [businessModels[modelName]];
    }

    let mappings = Mappings.getAvailableMappings(this.attr('modelName'));
    let types = _.sortBy(mappings, 'model_singular');

    if (!this.attr('criteria.objectName')) {
      this.attr('criteria.objectName', _.head(types).model_singular);
    }

    return types;
  },
  /**
   * Returns a criteria title.
   * @return {string} - Criteria title.
   */
  title: function () {
    if (this.attr('root')) {
      return 'Mapped To';
    }
    return 'Where ' +
            businessModels[this.attr('modelName')].title_singular +
            ' is mapped to';
  },
  /**
   * Dispatches event meaning that the component should be removed from parent container.
   */
  remove: function () {
    this.dispatch('remove');
  },
  /**
   * Dispatches event meaning that the component should be transformed to Mapping Group.
   */
  createGroup: function () {
    this.dispatch('createGroup');
  },
  /**
   * Creates the child Mapping Criteria.
   */
  addRelevant: function () {
    this.attr('criteria.mappedTo',
      AdvancedSearch.create.mappingCriteria());
  },
  /**
   * Removes the child Mapping Criteria.
   */
  removeRelevant: function () {
    this.removeAttr('criteria.mappedTo');
  },
  /**
   * Transforms child Mapping Criteria to Mapping Group.
   */
  relevantToGroup: function () {
    this.attr('criteria.mappedTo',
      AdvancedSearch.create.group([
        this.attr('criteria.mappedTo'),
        AdvancedSearch.create.operator('AND'),
        AdvancedSearch.create.mappingCriteria(),
      ]));
  },
});

/**
 * Mapping Criteria is specific kind of Filter Item.
 */
export default can.Component.extend({
  tag: 'advanced-search-mapping-criteria',
  template: can.stache(template),
  leakScope: false,
  viewModel: viewModel,
});
