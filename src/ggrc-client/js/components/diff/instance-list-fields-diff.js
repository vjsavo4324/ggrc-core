/*
 Copyright (C) 2019 Google Inc., authors, and contributors
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import {getModelInstance} from '../../plugins/utils/models-utils';
import {buildModifiedListField} from '../../plugins/utils/object-history-utils';
import {REFRESH_PROPOSAL_DIFF} from '../../events/eventTypes';
import DiffBaseVM from './diff-base-vm';
import {reify} from './../../plugins/utils/reify-utils';
import template from './templates/instance-diff-items.stache';

const viewModel = DiffBaseVM.extend({
  modifiedFields: {},

  buildDiffObject() {
    const instance = this.attr('currentInstance');
    const modifiedKeys = can.Map.keys(this.attr('modifiedFields'));
    this.attr('diff', []);
    modifiedKeys.forEach((key) => {
      const currentVal = this.loadFieldList(instance.attr(key));
      const modifiedItem = this.attr('modifiedFields')[key];
      const modifiedVal = buildModifiedListField(currentVal, modifiedItem);

      const currentValPromise = this.fetchData(currentVal);
      const modifiedValPromise = this.fetchData(modifiedVal);

      Promise.all([currentValPromise, modifiedValPromise])
        .then((data) => {
          const diffItem = this.buildDisplayNames({
            attrName: key,
            currentVal: data[0],
            modifiedVal: data[1],
          });

          this.attr('diff').push(diffItem);
        });
    });
  },
  fetchData(values) {
    if (!values || !values.length) {
      return Promise.resolve([]);
    }

    const objectData = values.attr().map((item) =>
      getModelInstance(item.id, item.type, 'name'));

    return Promise.all(objectData);
  },
  buildDisplayNames(diffData) {
    const currentDisplayNames = this.getDisplayValue(diffData.currentVal);
    const modifiedDisplayNames = this.getDisplayValue(diffData.modifiedVal);
    const attrName = this.getAttrDisplayName(diffData.attrName);
    const diff = {
      attrName,
      currentVal: currentDisplayNames,
      modifiedVal: modifiedDisplayNames,
    };

    return diff;
  },
  getDisplayValue(value) {
    const displayNames = value.map((item) => this.getDisplayName(item));
    return displayNames.length ?
      displayNames.sort() :
      [this.attr('emptyValue')];
  },
  loadFieldList(values) {
    // get from cache
    return values.map((item) => reify(item));
  },
});

export default can.Component.extend({
  tag: 'instance-list-fields-diff',
  template: can.stache(template),
  leakScope: true,
  viewModel: viewModel,
  events: {
    buildDiff() {
      const instance = this.viewModel.attr('currentInstance');
      const modifiedFields = this.viewModel.attr('modifiedFields');
      if (!modifiedFields || !instance) {
        return;
      }
      this.viewModel.buildDiffObject();
    },
    inserted() {
      this.buildDiff();
    },
    [`{viewModel.currentInstance} ${REFRESH_PROPOSAL_DIFF.type}`]() {
      this.buildDiff();
    },
  },
});
