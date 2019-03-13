/*
    Copyright (C) 2019 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

$.fn.extend({
  load: function (callback) {
    $(window).on('load', callback);
  },

  // Returns viewModel instsnce from element of Component
  viewModel: function () {
    return $(this).data('viewModel') || new can.Map();
  },

  /*
  * @function jQuery.fn.controls jQuery.fn.controls
  * @parent can.Control.plugin
  * @description Get the Controls associated with elements.
  * @signature `jQuery.fn.controls([type])`
  * @param {String|can.Control} [control] The type of Controls to find.
  * @return {can.Control} The controls associated with the given elements.
  *
  * @body
  * When the widget is initialized, the plugin control creates an array
  * of control instance(s) with the DOM element it was initialized on using
  * [can.data] method.
  *
  * The `controls` method allows you to get the control instance(s) for any element
  * either by their type or pluginName.
  *
  *      var MyBox = can.Control({
  *          pluginName : 'myBox'
  *      }, {});
  *
  *      var MyClock = can.Control({
  *          pluginName : 'myClock'
  *      }, {});
  *
  *
  * //- Inits the widgets
      * $('.widgets:eq(0)').myBox();
      * $('.widgets:eq(1)').myClock();
      *
      * $('.widgets').controls() //-> [ MyBox, MyClock ]
      *     $('.widgets').controls('myBox') // -> [MyBox]
      *     $('.widgets').controls(MyClock) // -> MyClock
      *
      */
  controls: function () {
    let controllerNames = can.makeArray(arguments);
    let instances = [];
    let controls;
    // check if arguments
    this.each(function () {
      controls = $(this).data('controls');
      if (!controls) {
        return;
      }
      for (let i = 0; i < controls.length; i++) {
        let c = controls[i];
        if (!controllerNames.length) {
          instances.push(c);
        }
      }
    });
    return instances;
  },

  /*
   * @function jQuery.fn.control jQuery.fn.control
   * @parent can.Control.plugin
   * @description Get the Control associated with elements.
   * @signature `jQuery.fn.control([type])`
   * @param {String|can.Control} [control] The type of Control to find.
   * @return {can.Control} The first control found.
   *
   * @body
   * This is the same as [jQuery.fn.controls $().controls] except that
   * it only returns the first Control found.
   *
   * //- Init MyBox widget
      * $('.widgets').my_box();
      *
      * <div class="widgets my_box" />
      *
      * $('.widgets').controls() //-> MyBox
      */
  control: function (control) {
    return this.controls.apply(this, arguments)[0];
  },
});
