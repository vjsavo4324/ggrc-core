/*
 Copyright (C) 2019 Google Inc., authors, and contributors
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import Pagination from '../../base-objects/pagination';
import template from './templates/related-revisions.stache';
import './related-revisions-item';
import Revision from '../../../models/service-models/revision.js';

export default can.Component.extend({
  tag: 'related-revisions',
  template: can.stache(template),
  leakScope: true,
  viewModel: {
    define: {
      paging: {
        value: function () {
          return new Pagination({pageSizeSelect: [5, 10, 15]});
        },
      },
    },
    instance: null,
    lastRevision: {},
    visibleRevisions: [],
    revisions: [],
    loading: false,
    setVisibleRevisions() {
      const visibleRevisions = this.attr('revisions')
        .slice(...this.attr('paging.limits'));
      this.attr('visibleRevisions', visibleRevisions);

      // recalculate pages
      this.attr('paging.total', this.attr('revisions').length);
    },
    loadRevisions() {
      if (!this.attr('instance')) {
        return;
      }

      this.attr('loading', true);

      this.buildRevisionRequest('resource').then((data) => {
        let revisions;
        this.attr('loading', false);

        if (!data || !data.length) {
          return;
        }

        // skip last revision. it's current state of object
        revisions = data.slice(1, data.length);
        this.attr('paging.total', revisions.length);
        this.attr('revisions', revisions);

        // get first because revisions have desc sorting
        this.attr('lastRevision', data[0]);

        this.setVisibleRevisions();
      });
    },
    buildRevisionRequest(attr) {
      const query = {__sort: '-updated_at'};
      query[attr + '_type'] = this.attr('instance.type');
      query[attr + '_id'] = this.attr('instance.id');
      return Revision.findAll(query);
    },
  },
  events: {
    inserted() {
      this.viewModel.loadRevisions();
    },
    '{viewModel.paging} current'() {
      this.viewModel.setVisibleRevisions();
    },
    '{viewModel.paging} pageSize'() {
      this.viewModel.setVisibleRevisions();
    },
    '{viewModel.instance} modelAfterSave'() {
      this.viewModel.loadRevisions();
    },
  },
});
