/*
    Copyright (C) 2019 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import template from './cycle-task-objects.stache';
import Mappings from '../../../models/mappers/mappings';

const viewModel = can.Map.extend({
  parentInstance: null,
  mappedObjects: [],
});

const init = function (element) {
  const binding = Mappings
    .getBinding(
      'info_related_objects',
      this.viewModel.parentInstance
    );

  binding.refresh_instances()
    .then((mappedObjects) => {
      this.viewModel.attr('mappedObjects').replace(mappedObjects);
    });

  // We are tracking binding changes, so mapped items update accordingly
  binding.list.on('change', () => {
    this.viewModel.attr('mappedObjects').replace(binding.list);
  });
};

export default can.Component.extend({
  tag: 'cycle-task-objects',
  template: can.stache(template),
  leakScope: true,
  viewModel,
  init,
});
