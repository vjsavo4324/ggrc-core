/*
  Copyright (C) 2019 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import template from './add-tab-button.stache';
import {
  getPageType,
  isMyWork,
  isAllObjects,
} from '../../plugins/utils/current-page-utils';
import Permission from '../../permission';
import Mappings from '../../models/mappers/mappings';
import '../questionnaire-mapping-link/questionnaire-mapping-link';

const viewModel = can.Map.extend({
  define: {
    isAuditInaccessibleAssessment: {
      get() {
        let audit = this.attr('instance.audit');
        let type = this.attr('instance.type');
        let result = (type === 'Assessment') &&
          !!audit &&
          !Permission.is_allowed_for('read', audit);
        return result;
      },
    },
    shouldShow: {
      get() {
        let instance = this.attr('instance');

        return !this.attr('isAuditInaccessibleAssessment')
          && Permission.is_allowed_for('update', instance)
          && !instance.attr('archived')
          && !isMyWork()
          && !isAllObjects()
          && !['Person', 'Evidence'].includes(getPageType())
          && this.attr('widgetList.length') > 0;
      },
    },
  },
  instance: null,
  widgetList: null,
  addTabTitle: '',
  isAllowedToMap(target) {
    let source = this.attr('instance');
    return Mappings.allowedToMap(source, target);
  },
});

export default can.Component.extend({
  tag: 'add-tab-button',
  template: can.stache(template),
  leakScope: true,
  viewModel,
  events: {
    // top nav dropdown position
    '.dropdown-toggle click'(el) {
      let $dropdown = this.element.find('.dropdown-menu');
      let leftPos = el.offset().left;
      let winWidth = $(window).width();

      if (winWidth - leftPos < 400) {
        $dropdown.addClass('right-pos');
      } else {
        $dropdown.removeClass('right-pos');
      }
    },
  },
  helpers: {
    shouldCreateObject(instance, modelShortName, options) {
      if (modelShortName() === 'Audit' &&
        instance().type === 'Program') {
        return options.fn(options.contexts);
      }

      return options.inverse(options.contexts);
    },
    canMapObject(modelShortName, options) {
      if (this.isAllowedToMap(modelShortName())) {
        return options.fn(options.contexts);
      }
      return options.inverse(options.contexts);
    },
    isMappableExternally(instance, modelShortName, options) {
      let source = instance().type;
      let destination = modelShortName();
      if (Mappings.shouldBeMappedExternally(source, destination)) {
        return options.fn(options.contexts);
      }
      return options.inverse(options.contexts);
    },
  },
});
