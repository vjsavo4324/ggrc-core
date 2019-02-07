/*
    Copyright (C) 2019 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

export default can.Component.extend({
  tag: 'unarchive-link',
  template: can.stache('<a href="#"><content></content></a>'),
  leakScope: true,
  viewModel: {
    notify: '@',
    instance: null,
    notifyText: 'was unarchived successfully',
  },
  events: {
    'a click': function (el, event) {
      let instance = this.viewModel.attr('instance');
      let notifyText = instance.display_name() + ' ' +
        this.viewModel.attr('notifyText');

      event.preventDefault();

      if (instance && instance.attr('archived')) {
        instance.attr('archived', false);
        instance.save()
          .then(function () {
            if (this.viewModel.attr('notify')) {
              $('body').trigger('ajax:flash', {success: notifyText});
            }
          }.bind(this));
      }
    },
  },
});
