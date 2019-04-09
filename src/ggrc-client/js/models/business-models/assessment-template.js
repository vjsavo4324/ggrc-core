/*
 Copyright (C) 2019 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import Cacheable from '../cacheable';
import {getPageInstance} from '../../plugins/utils/current-page-utils';
import refetchHash from '../mixins/refetch-hash';
import assessmentIssueTracker from '../mixins/assessment-issue-tracker';
import Stub from '../stub';

/**
 * A model describing a template for the newly created Assessment objects.
 *
 * This is useful when creating multiple similar Assessment objects. Using an
 * AssessmentTemplate helps avoiding repeatedly defining the same set of
 * Assessment object properties for each new instance.
 */
export default Cacheable.extend({
  root_object: 'assessment_template',
  root_collection: 'assessment_templates',
  model_singular: 'AssessmentTemplate',
  model_plural: 'AssessmentTemplates',
  title_singular: 'Assessment Template',
  title_plural: 'Assessment Templates',
  table_singular: 'assessment_template',
  table_plural: 'assessment_templates',
  mixins: [
    refetchHash,
    assessmentIssueTracker,
  ],
  findOne: 'GET /api/assessment_templates/{id}',
  findAll: 'GET /api/assessment_templates',
  update: 'PUT /api/assessment_templates/{id}',
  destroy: 'DELETE /api/assessment_templates/{id}',
  create: 'POST /api/assessment_templates',
  is_custom_attributable: false,
  attributes: {
    context: Stub,
  },
  defaults: {
    test_plan_procedure: true,
    template_object_type: 'Control',
    default_people: {
      assignees: 'Principal Assignees',
      verifiers: 'Auditors',
    },
    status: 'Draft',
  },
  statuses: ['Draft', 'Deprecated', 'Active'],
  tree_view_options: {
    attr_list: [{
      attr_title: 'Title',
      attr_name: 'title',
      order: 10,
    }, {
      attr_title: 'State',
      attr_name: 'status',
      order: 20,
    }, {
      attr_title: 'Code',
      attr_name: 'slug',
      order: 30,
    }, {
      attr_title: 'Last Updated Date',
      attr_name: 'updated_at',
      order: 70,
    }, {
      attr_title: 'Last Updated By',
      attr_name: 'modified_by',
      order: 71,
    }],
    add_item_view: 'assessment_templates/tree_add_item',
  },

  /**
   * Initialize the newly created object instance. Validate that its title is
   * non-blank and its default assignees / verifiers lists are set if
   * applicable.
   */
  init: function () {
    this._super(...arguments);
    this.validateNonBlank('title');

    this.validateListNonBlank(
      'default_people.assignees',
      function () {
        return this.attr('default_people.assignees') instanceof can.List;
      }
    );
    this.validateListNonBlank(
      'default_people.verifiers',
      function () {
        return this.attr('default_people.verifiers') instanceof can.List;
      }
    );
    this.validate(
      'issue_tracker_component_id',
      function () {
        if (this.attr('can_use_issue_tracker') &&
          this.attr('issue_tracker.enabled') &&
          !this.attr('issue_tracker.component_id')) {
          return 'cannot be blank';
        }
      }
    );
  },
}, {
  /**
   * An event handler when the add/edit form is about to be displayed.
   *
   * It builds a list of all object types used to populate the corresponding
   * dropdown menu on the form.
   * It also deserializes the default people settings so that those form
   * fields are correctly populated.
   */
  form_preload: function () {
    const pageInstance = getPageInstance();
    if (pageInstance && (!this.audit || !this.audit.id || !this.audit.type)) {
      if (pageInstance.type === 'Audit') {
        this.attr('audit', pageInstance);
      }
    }

    if (!this.custom_attribute_definitions) {
      this.attr('custom_attribute_definitions', new can.List());
    }
  },
});
