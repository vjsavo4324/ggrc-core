/*
    Copyright (C) 2019 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import '../components/info-pin-buttons/info-pin-buttons';
import '../components/questions-link/questions-link';
import '../components/info-pane/info-pane-footer';
import '../components/assessment/info-pane/info-pane';
import '../components/folder-attachments-list/folder-attachments-list';
import '../components/issue-tracker/info-issue-tracker-fields';
import '../components/issue-tracker/generate-issues-in-bulk-button';
import '../components/comment/comments-section';
import '../components/object-list-item/document-object-list-item';
import '../components/object-list-item/editable-document-object-list-item';
import '../components/show-related-assessments-button/show-related-assessments-button';
import '../components/related-objects/proposals/related-proposals';
import '../components/related-objects/proposals/related-proposals-item';
import '../components/related-objects/revisions/related-revisions';
import '../components/snapshotter/revisions-comparer';
import '../components/snapshotter/snapshot-comparer-config';
import '../components/revision-history/restore-revision';
import '../components/unarchive_link';
import '../components/sort/sort';
import '../components/object-review/object-review';
import '../components/review-state/review-state';
import '../components/redirects/proposable-control/proposable-control';
import '../components/redirects/proposable-attribute/proposable-attribute';
import '../components/general-page-header/general-page-header';
import * as TreeViewUtils from '../plugins/utils/tree-view-utils';
import {confirm} from '../plugins/utils/modals';
import {getInstanceView} from '../plugins/utils/object-history-utils';
import {getPageInstance} from '../plugins/utils/current-page-utils';

export const pinContentHiddenClass = 'pin-content--hidden';
export const pinContentMaximizedClass = 'pin-content--maximized';
export const pinContentMinimizedClass = 'pin-content--minimized';

export default can.Control.extend({
  defaults: {
    view: GGRC.templates_path + '/base_objects/info.stache',
  },
}, {
  init: function (el, options) {
    this.unsetInstance();
  },
  isPinVisible() {
    return !this.element.hasClass(pinContentHiddenClass);
  },
  findOptions: function (el) {
    return el.closest('.tree-item-element').viewModel();
  },
  hideInstance: function () {
    this.unsetInstance();
    $(window).trigger('resize');
  },
  unsetInstance: function () {
    this.element
      .addClass(pinContentHiddenClass)
      .removeClass(`${pinContentMaximizedClass} ${pinContentMinimizedClass}`)
      .html('');
  },
  setHtml: function (opts, view, confirmEdit, options, maximizedState) {
    let instance = opts.attr('instance');
    let parentInstance = opts.attr('parent_instance');
    let self = this;
    import(/* webpackChunkName: "modalsCtrls" */'./modals')
      .then(() => {
        let context = {
          instance: instance,
          isSnapshot: !!instance.snapshot || instance.isRevision,
          parentInstance: parentInstance,
          model: instance.class,
          confirmEdit: confirmEdit,
          is_info_pin: true,
          options: options,
          result: options.result,
          page_instance: getPageInstance(),
          maximized: maximizedState,
          onChangeMaximizedState: function () {
            return self.changeMaximizedState.bind(self);
          },
          onClose: function () {
            return self.close.bind(self);
          },
        };

        $.ajax({
          url: view,
          dataType: 'text',
        }).then((view) => {
          let frag = can.stache(view)(context);
          this.element.html(frag);
        });
      });
  },
  prepareView: function (opts, el, maximizedState) {
    let instance = opts.attr('instance');
    let options = this.findOptions(el);
    let populatedOpts = opts.attr('options');
    let confirmEdit = instance.class.confirmEditModal || {};
    let view = getInstanceView(instance);

    if (populatedOpts && !options.attr('result')) {
      options = populatedOpts;
    }

    if (!_.isEmpty(confirmEdit)) {
      confirmEdit.confirm = this.confirmEdit;
    }

    this.setHtml(opts, view, confirmEdit, options, maximizedState);
  },
  setInstance: function (opts, el, maximizedState) {
    let instance = opts.attr('instance');
    let infoPaneOpenDfd = $.Deferred();
    let isSubtreeItem = opts.attr('options.isSubTreeItem');

    opts.attr('options.isDirectlyRelated',
      !isSubtreeItem ||
      TreeViewUtils.isDirectlyRelated(instance));

    this.prepareView(opts, el, maximizedState);

    if (instance.info_pane_preload) {
      instance.info_pane_preload();
    }

    this.changeMaximizedState(maximizedState);

    // Temporary solution...
    setTimeout(infoPaneOpenDfd.resolve, 1000);

    return infoPaneOpenDfd;
  },
  changeMaximizedState(maximizedState) {
    this.element
      .removeClass(`${pinContentMaximizedClass} ${pinContentMinimizedClass}`)
      .removeClass(pinContentHiddenClass);

    if (maximizedState) {
      this.element.addClass(pinContentMaximizedClass);
    } else {
      this.element.addClass(pinContentMinimizedClass);
    }
  },
  updateInstance: function (selector, instance) {
    let vm = this.element.find(selector).viewModel();

    vm.attr('instance', instance);
  },
  setLoadingIndicator: function (selector, isLoading) {
    this.element.toggleClass('loading');

    this.element.find(selector)
      .viewModel()
      .attr('isLoading', isLoading);
  },
  confirmEdit: function (instance, modalDetails) {
    let confirmDfd = $.Deferred();
    let renderer = can.stache(modalDetails.description);
    confirm({
      modal_description: renderer(instance).textContent,
      modal_confirm: modalDetails.button,
      modal_title: modalDetails.title,
      button_view: GGRC.templates_path + '/quick_form/confirm_buttons.stache',
    }, confirmDfd.resolve);
    return confirmDfd;
  },
  close: function () {
    let visibleWidget = $('.widget-area .widget:visible');

    visibleWidget.find('.item-active')
      .removeClass('item-active');

    this.unsetInstance();
  },
  /**
   * Checks if there are modals on top of the info pane.
   * @return {boolean} - true if there are modals on top of the info pane else
   *  false.
   */
  existModals() {
    return (
      $('.modal:visible').length > 0 ||
      $('[role=dialog]:visible').length > 0
    );
  },
  /**
   * Checks if $target is an element wherein shouldn't be closed the info pane
   * with help the escape key.
   * @param {jQuery} $target - an jQuery element.
   * @return {boolean} - true if the escape key shouldn't be processed
   *  otherwise false.
   */
  isEscapeKeyException($target) {
    const insideInfoPane = $target.closest('.pin-content').length > 0;
    const excludeForEscapeKey = ['button', '[role=button]', '.btn', 'input',
      'textarea'];
    const isExcludingControl = _.some(excludeForEscapeKey, (typeName) =>
      $target.is(typeName)
    );
    return (
      insideInfoPane &&
      (
        isExcludingControl ||
        $target.attr('contentEditable') === 'true'
      )
    );
  },
  ' scroll': function (el, ev) {
    const header = this.element.find('.pane-header');
    const scrollTop = el.scrollTop();
    const prevScrollTop = el.data('scrollTop') || 0;
    const headerOuterHeight = header.outerHeight();

    if (!prevScrollTop) {
      header.css({top: -headerOuterHeight});
    }

    if (scrollTop === 0) {
      header.removeClass('pane-header_visible');
    } else
    if (scrollTop > header.outerHeight()) {
      if (scrollTop > prevScrollTop) {
        // scroll down
        if (header.hasClass('pane-header_visible')) {
          header.removeClass('pane-header_visible');
          header.addClass('pane-header_hidden');
        }

        // hide menu when scrolling down
        let dropdownMenu = header.find('.details-wrap');
        dropdownMenu.removeClass('open');
      } else if (scrollTop < prevScrollTop) {
        // scroll top
        header.removeClass('pane-header_hidden');
        header.addClass('pane-header_visible');
      }
    }

    el.data('scrollTop', scrollTop);
  },
  '{window} keyup'(el, event) {
    const ESCAPE_KEY_CODE = 27;
    const $target = $(event.target);
    const escapeKeyWasPressed = event.keyCode === ESCAPE_KEY_CODE;

    const close = (
      escapeKeyWasPressed &&
      this.isPinVisible() &&
      !this.existModals() &&
      !this.isEscapeKeyException($target)
    );

    if (close) {
      this.close();
      event.stopPropagation();
    }
  },
});
