/*
    Copyright (C) 2019 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/
(function ($, can) {
  let originComponentInit = can.Component.prototype.init;

  // Returns a function which will be halted unless `this.element` exists
  // - useful for callbacks which depend on the controller's presence in the DOM
  can.Control.prototype._ifNotRemoved = function (fn) {
    let isPresent = this.element;
    return function () {
      return isPresent ? fn.apply(this, arguments) : null;
    };
  };

  /*
  can.camelCaseToUnderscore = function (string) {
    if (!_.isString(string)) {
      throw new TypeError('Invalid type, string required.');
    }
    return _.snakeCase(string);
  };
  */

  // Add viewModel instance to element's data of component
  can.Component.prototype.init = function (el) {
    $(el).data('viewModel', this.viewModel);
    originComponentInit.apply(this, arguments);
  };

  // Add control instance to element's data of control
  can.Control.initElement = function (ctrlInstance) {
    const $el = $(ctrlInstance.element);
    ctrlInstance.$element = $el;
    if (!$el.data('controls') || !$el.data('controls').length) {
      $el.data('controls', [ctrlInstance]);
    } else {
      $el.data('controls').push(ctrlInstance);
    }
  };
})(jQuery, can);
