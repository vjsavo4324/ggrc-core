/*
  Copyright (C) 2019 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import * as module from '../../../plugins/utils/tree-view-utils';
import * as aclUtils from '../../../plugins/utils/acl-utils';
import * as ImportExportUtils from '../../../plugins/utils/import-export-utils';
import * as QueryApiUtils from '../../../plugins/utils/query-api-utils';
import Mappings from '../../../models/mappers/mappings';

import CycleTaskGroupObjectTask from '../../../models/business-models/cycle-task-group-object-task';
import Control from '../../../models/business-models/control';

describe('TreeViewUtils module', function () {
  'use strict';

  let method;
  let origPageType;

  beforeAll(function () {
    origPageType = GGRC.pageType;
    GGRC.pageType = 'MY_WORK';
  });

  afterAll(function () {
    GGRC.pageType = origPageType;
  });

  describe('getColumnsForModel() method', function () {
    let origCustomAttrDefs;
    let origAttrs;

    beforeAll(function () {
      method = module.getColumnsForModel;

      spyOn(aclUtils, 'getRolesForType').and.returnValue([
        {id: 9, name: 'Role 9', object_type: 'Audit'},
        {id: 3, name: 'Role 3', object_type: 'Audit'},
      ]);

      origAttrs = [].concat(CycleTaskGroupObjectTask
        .tree_view_options.display_attr_names);

      origCustomAttrDefs = GGRC.custom_attr_defs;
      GGRC.custom_attr_defs = [{
        id: 16, attribute_type: 'Text',
        definition_type: 'market', title: 'CA def 16',
      }, {
        id: 17, attribute_type: 'Rich Text',
        definition_type: 'market', title: 'CA def 17',
      }, {
        id: 5, attribute_type: 'Text',
        definition_type: 'policy', title: 'CA def 5',
      }, {
        id: 11, attribute_type: 'Text',
        definition_type: 'audit', title: 'CA def 11',
      }];
    });

    afterAll(function () {
      GGRC.custom_attr_defs = origCustomAttrDefs;
      CycleTaskGroupObjectTask
        .tree_view_options.display_attr_names =
          origAttrs;
    });

    it('includes custom roles info in the result ', function () {
      let result = method('Audit', null);
      result = _.filter(result.available, {attr_type: 'role'});

      ['Role 3', 'Role 9'].forEach(function (title) {
        let expected = {
          attr_type: 'role',
          attr_title: 'Role 9',
          attr_name: 'Role 9',
          attr_sort_field: 'Role 9',
        };
        expect(result).toContain(jasmine.objectContaining(expected));
      });
    });

    it('Sets disable_sorting flag to true for the GCAs with "Rich Text" type ',
      function () {
        let expected = {
          attr_type: 'custom',
          attr_title: 'CA def 17',
          attr_name: 'CA def 17',
          attr_sort_field: 'CA def 17',
          disable_sorting: true,
        };

        let result = method('Market', null);
        result = _.filter(result.available, {attr_type: 'custom'});

        expect(result).toContain(jasmine.objectContaining(expected));
      });

    it(`Sets disable_sorting flag to false for the GCAs
     with not "Rich Text" type `,
    function () {
      let expected = {
        attr_type: 'custom',
        attr_title: 'CA def 16',
        attr_name: 'CA def 16',
        attr_sort_field: 'CA def 16',
        disable_sorting: false,
      };

      let result = method('Market', null);
      result = _.filter(result.available, {attr_type: 'custom'});

      expect(result).toContain(jasmine.objectContaining(expected));
    });
  });

  describe('getSortingForModel() method', function () {
    let noDefaultSortingModels = [
      'Cycle',
      'TaskGroup',
      'TaskGroupTask',
      'CycleTaskGroupObjectTask',
    ];

    it('returns default sorting configuration', function () {
      let result = module.getSortingForModel('Audit');

      expect(result).toEqual({key: 'updated_at', direction: 'desc'});
    });

    it('returns empty sorting configuration', function () {
      noDefaultSortingModels.forEach((model) => {
        let result = module.getSortingForModel(model);

        expect(result).toEqual({key: null, direction: null});
      });
    });
  });

  describe('getModelsForSubTier() method', function () {
    let origFilter;

    beforeAll(function () {
      origFilter = Control.sub_tree_view_options.default_filter;
    });

    afterAll(function () {
      Control.sub_tree_view_options.default_filter = origFilter;
    });

    it('gets selected models from model\'s default_filter when available',
      function () {
        let result;

        Control.sub_tree_view_options.default_filter = ['Audit'];

        result = module.getModelsForSubTier('Control');
        expect(result.available.length).toEqual(32);
        expect(result.selected.length).toEqual(1);
        expect(result.selected[0]).toEqual('Audit');
      });

    it('returns all available models as selected when ' +
      'model\'s default_filter is not available', function () {
      let result;

      Control.sub_tree_view_options.default_filter = null;

      result = module.getModelsForSubTier('Control');
      expect(result.available.length).toEqual(32);
      expect(result.selected.length).toEqual(32);
    });

    it('gets available models from Mappings for CycleTaskGroupObjectTask',
      () => {
        spyOn(Mappings, 'getMappingList').and.returnValue(['Audit', 'Control']);
        let result = module.getModelsForSubTier('CycleTaskGroupObjectTask');
        expect(result.available.length).toEqual(2);
      });
  });

  describe('startExport() method', () => {
    let modelName;
    let parent;
    let filter;
    let request;

    beforeEach(() => {
      spyOn(ImportExportUtils, 'runExport');
      spyOn(ImportExportUtils, 'fileSafeCurrentDate');
      spyOn(QueryApiUtils, 'buildParam');
      spyOn(module, 'makeRelevantExpression')
        .and.returnValue('testRelevantExpression');

      modelName = 'testModelName';
      parent = {
        type: 'testParentType',
        id: 'testParentId',
      };
      filter = {testFilter: true};
      request = new can.List();
    });

    it('builds request params correctly', () => {
      module.startExport(modelName, parent, filter, request);

      expect(QueryApiUtils.buildParam).toHaveBeenCalledWith(
        modelName,
        {},
        {type: parent.type, id: parent.id, operation: 'owned'},
        'all',
        filter);
    });

    it('runs export correctly', () => {
      request = new can.List(['testRequest1']);
      ImportExportUtils.fileSafeCurrentDate
        .and.returnValue('testFileSafeCurrentDate');
      QueryApiUtils.buildParam
        .and.returnValue('testRequest2');

      module.startExport(modelName, parent, filter, request);

      expect(ImportExportUtils.runExport).toHaveBeenCalledWith({
        objects: ['testRequest1', 'testRequest2'],
        current_time: 'testFileSafeCurrentDate',
        exportable_objects: [1],
      });
    });
  });
});
