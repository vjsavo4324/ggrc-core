/*
 Copyright (C) 2019 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import * as StateUtils from '../../plugins/utils/state-utils';
import {getCounts} from '../../plugins/utils/widgets-utils';
import TreeLoader from './tree-loader';
import TreeViewNode from './tree-view-node';
import TreeViewOptions from './tree-view-options';
import Mappings from '../../models/mappers/mappings';
import * as canEvent from 'can-event';

const TreeViewControl = TreeLoader.extend({
  // static properties
  defaults: {
    model: null,
    show_view: null,
    show_header: false,
    add_item_view: null,
    parent: null,
    list: null,
    filteredList: [],
    single_object: false,
    find_params: {},
    fields: [],
    filter_states: [],
    sortable: true,
    start_expanded: false, // true
    find_function: null,
    options_property: 'tree_view_options',
    child_options: [], // this is how we can make nested configs. if you want to use an existing
    // example child option:
    // { property: "controls", model: Control, }
    // { parent_find_param: "system_id" ... }
    scroll_page_count: 1, // pages above and below viewport
    is_subtree: false,
    subTreeElementsLimit: 20,
    limitDeepOfTree: 2,
  },
  do_not_propagate: [
    'header_view',
    'add_item_view',
    'list',
    'original_list',
    'single_object',
    'find_function',
    'find_all_deferred',
  ],
}, {
  // prototype properties
  setup: function (el, opts) {
    let defaultOptions;
    let optionsProperty;
    let defaults = this.constructor.defaults;
    if (typeof this._super === 'function') {
      this._super(el);
    }

    optionsProperty = opts.options_property || defaults.options_property;
    defaultOptions = opts.model[optionsProperty] || {};

    this.options = new can.Map(defaults).attr(defaultOptions).attr(opts);
    if (opts instanceof can.Map) {
      this.options = Object.assign(this.options, opts);
    }
  },

  init: function (el, opts) {
    can.Control.initElement(this);

    let states = StateUtils
      .getStatesForModel(this.options.model.model_singular);

    let filterStates = states.map(function (state) {
      return {value: state};
    });

    this.options.attr('filter_states', filterStates);

    const widget = this.$element.closest('.widget');

    if (widget && !widget.hasClass('tree-view-control-attached')) {
      widget.on('widget_hidden', this.widget_hidden.bind(this));
      widget.on('widget_shown', this.widget_shown.bind(this));

      widget.addClass('tree-view-control-attached');
    }

    this.$element.uniqueId();

    this.options.attr('is_subtree',
      this.element && this.$element.closest('.inner-tree').length > 0);

    if (!this.options.scroll_element) {
      this.options.attr('scroll_element', $('.object-area'));
    }

    // Override nested child options for allow_* properties
    let allowed = {};
    this.options.each(function (item, prop) {
      if (prop.indexOf('allow') === 0 && item === false) {
        allowed[prop] = item;
      }
    });
    this.options.attr('child_options', this.options.child_options.slice(0));
    _.forEach(this.options.child_options, function (options, i) {
      this.options.child_options.attr(i,
        new can.Map(Object.assign(options.attr(), allowed)));
    }.bind(this));

    this._attached_deferred = $.Deferred();
    if (this.element && this.$element.closest('body').length) {
      this._attached_deferred.resolve();
    }

    // Make sure the parent_instance is not a computable
    if (typeof this.options.parent_instance === 'function') {
      this.options.attr('parent_instance', this.options.parent_instance());
    }
  },
  ' inserted': function () { // eslint-disable-line quote-props
    this._attached_deferred.resolve();
  },
  init_view: function () {
    let dfds = [];
    let statusControl;

    if (this.options.header_view && this.options.show_header) {
      dfds.push(
        $.when(this.options, $.ajax({
          url: this.options.header_view,
          dataType: 'text',
        })).then((ctx, view) => {
          return can.stache(view[0])(ctx);
        }).then(
          this._ifNotRemoved((frag) => {
            this.$element.before(frag);

            statusControl = this.$element.parent()
              .find('.tree-filter__status-wrap');
            // set state filter (checkboxes)
            can.bind.call(statusControl.ready(() => {
              let selectStateList = this.options.attr('selectStateList');

              this.options.attr('filter_states').forEach((item) => {
                if (selectStateList.indexOf(item.value) > -1) {
                  item.attr('checked', true);
                }
              });
            }));
          })));
    }

    this.init_count();

    this._init_view_deferred = $.when.apply($.when, dfds);
    return this._init_view_deferred;
  },

  init_count: function () {
    let self = this;
    let options = this.options;
    let countsName = options.countsName || options.model.model_singular;

    if (this.options.list_loader) {
      this.options.list_loader(this.options.parent_instance)
        .then(function (list) {
          return can.compute(function () {
            return list.attr('length');
          });
        })
        .then(function (count) {
          if (self.element) {
            getCounts().attr(countsName, count());
          }
          count.bind('change', self._ifNotRemoved(function () {
            getCounts().attr(countsName, count());
          }));
        });
    }
  },

  fetch_list: function () {
    if (this.find_all_deferred) {
      //  Skip, because already done, e.g., display() already called
      return this.find_all_deferred;
    }
    if (can.isEmptyObject(this.options.find_params.serialize())) {
      this.options.find_params.attr(
        'id', this.options.parent_instance ?
          this.options.parent_instance.id : undefined);
    }

    if (this.options.mapping) {
      if (this.options.parent_instance === undefined) {
        // TODO investigate why is this method sometimes called twice
        return undefined; // not ready, will try again
      }
      let binding = Mappings.getBinding(
        this.options.mapping,
        this.options.parent_instance);
      this.find_all_deferred = binding.refresh_list();
    } else if (this.options.list_loader) {
      this.find_all_deferred =
        this.options.list_loader(this.options.parent_instance);
    } else {
      console.warn(`Unexpected code path ${this}`);
    }

    return this.find_all_deferred;
  },

  /*
    * Removes items from the list by ids
    * @param  {can.List}      list             list of items
    * @param  {Array{Number}} removedItemsIds  array of item ids
    */
  removeFromList: function (list, removedItemsIds) {
    // Since list items have slightly different format,
    // we are lookig for instance property in possible places
    let itemsToKeep = list.filter((item) => {
      let inst = item && item.options && item.options.attr('instance') ||
        item.attr('instance');

      return !_.includes(removedItemsIds, inst.attr('id'));
    });
    list.replace(itemsToKeep);
  },

  prepare_child_options: function (v, forceReload) {
    //  v may be any of:
    //    <model_instance>
    //    { instance: <model instance>, mappings: [...] }
    //    <TreeOptions>
    let tmp;
    let that = this;
    let original = v;
    if (v._child_options_prepared && !forceReload) {
      return v._child_options_prepared;
    }
    if (!(v instanceof TreeViewOptions)) {
      tmp = v;
      v = new TreeViewOptions();
      v.attr('instance', tmp);
      this.options.each(function (val, k) {
        if (!_.includes(that.constructor.do_not_propagate, k)) {
          v.attr(k, val);
        }
      });
    }
    if (!(v.instance instanceof can.Model)) {
      if (v.instance.instance instanceof can.Model) {
        v.attr('result', v.instance);
        v.attr('mappings', v.instance.mappings_compute());
        v.attr('instance', v.instance.instance);
      } else {
        v.attr('instance', this.options.model.model(v.instance));
      }
    }
    v.attr('child_count', can.compute(function () {
      let totalChildren = 0;
      if (v.attr('child_options')) {
        _.forEach(v.attr('child_options'), function (childCptions) {
          let list = childCptions.attr('list');
          if (list) {
            totalChildren += list.attr('length');
          }
        });
      }
      return totalChildren;
    }));
    original._child_options_prepared = v;
    return v;
  },

  '{original_list} remove': function (list, ev, removedItems, index) {
    let removedItemsIds = removedItems.map((remItem) => {
      return remItem.attr('id');
    });

    this.removeFromList(this.options.list, removedItemsIds);
    this.removeFromList(this.options.filteredList, removedItemsIds);

    // NB: since row element are not rendered with template and binded element
    // not always reflected in the filteredList ( for newly created items )
    // we are just removeing the items from the lists and removing the DOM
    // elements by ids
    removedItemsIds.forEach((id) => {
      this.$element
        .find(`.tree-view-node[data-object-id="${id}"]`)
        .remove();
    });
  },

  '{original_list} add': function (list, ev, newVals, index) {
    let that = this;
    let realAdd = [];

    _.forEach(newVals, function (newVal) {
      if (that.element) {
        realAdd.push(newVal);
      }
    });
    this.enqueue_items(realAdd);
  },
  // add child options to every item (TreeViewOptions instance) in the drawing list at this level of the tree.
  add_child_lists: function (list) {
    let that = this;
    let currentList = can.makeArray(list);
    let listWindow = [];
    let finalDfd;
    let queue = [];
    let BATCH = 200;
    let opId = this._add_child_lists_id = (this._add_child_lists_id || 0) + 1;

    currentList.forEach(function (item) {
      listWindow.push(item);
      if (listWindow.length >= BATCH) {
        queue.push(listWindow);
        listWindow = [];
      }
    });
    if (listWindow.length > 0) {
      queue.push(listWindow);
    }
    this.options.attr('filter_shown', 0);
    this.options.attr('filteredList', []);
    finalDfd = _.reduce(queue, function (dfd, listWindow) {
      return dfd.then(function () {
        let res = $.Deferred();
        if (that._add_child_lists_id !== opId) {
          return dfd;
        }
        setTimeout(function () {
          let draw;
          let drawDfd;
          if (that._add_child_lists_id !== opId) {
            return;
          }
          draw = that._ifNotRemoved(that.draw_items.bind(that));

          drawDfd = draw(listWindow);

          if (drawDfd) {
            drawDfd.then(res.resolve);
          } else {
            res.resolve();
          }
        }, 0);
        return res;
      });
    }, $.Deferred().resolve());

    finalDfd.done(this._ifNotRemoved(function () {
      let shown = this.$element[0].children.length;
      let count = this.options.list.length;
      // We need to hide `of` in case the numbers are same
      if (shown === count && shown > 0) {
        shown = false;
      } else {
        shown = shown.toString();
      }
      this.options.attr('filter_shown', shown);
      this.options.attr('filter_count', count.toString());
    }.bind(this)));
    return finalDfd;
  },
  draw_items: function (optionsList) {
    let items;
    let $footer = this.$element.children('.tree-item-add').first();
    let drawItemsDfds = [];
    let filteredItems = this.options.attr('filteredList') || [];
    let res;

    items = can.makeArray(optionsList);

    items = _.map(items, function (options) {
      let elem = document.createElement('li');
      let control = new TreeViewNode(elem, options);
      drawItemsDfds.push(control._draw_node_deferred);
      filteredItems.push(control);
      return control.element;
    });

    if ($footer.length) {
      $(items).insertBefore($footer);
    } else {
      this.$element.append(items);
    }
    if (this.options.sortable) {
      this.$element.sortable({element: 'li.tree-item', handle: '.drag'});
    }
    this.options.attr('filteredList', filteredItems);
    res = $.when(...drawItemsDfds);
    return res;
  },

  widget_hidden: function (event) {
    if (this.options.original_list) {
      this.clearList();
    }
    if (this._add_child_lists_id) {
      this._add_child_lists_id += 1;
    }

    return false;
  },

  widget_shown: function (event) {
    if (this.options.original_list) {
      setTimeout(this.reload_list.bind(this), 0);
    }
    return false;
  },

  '.edit-object modal:success': function (el, ev, data) {
    let model = el.closest('[data-model]').data('model');
    model.attr(data[model.constructor.root_object] || data);
    ev.stopPropagation();
  },

  reload_list: function (forceReload) {
    if (this.options.list === undefined || this.options.list === null) {
      return;
    }
    this._draw_list_deferred = false;
    this.find_all_deferred = false;
    this.options.list.replace([]);
    this.draw_list(this.options.original_list, forceReload);
    this.init_count();
  },

  clearList: function () {
    this.$element.children('.tree-item').remove();
  },
});

export default TreeViewControl;
