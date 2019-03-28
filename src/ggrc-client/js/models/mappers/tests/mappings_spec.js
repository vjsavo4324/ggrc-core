/*
 Copyright (C) 2019 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import * as Utils from '../../../plugins/utils/models-utils';
import Mappings from '../mappings';
import Permission from '../../../permission';

describe('Mappings', function () {
  let allTypes = [];
  let notMappableModels = [];
  let modules = {
    core: {
      models: [
        'AccessGroup',
        'AccountBalance',
        'Assessment',
        'AssessmentTemplate',
        'Audit',
        'Contract',
        'Control',
        'DataAsset',
        'Document',
        'Evidence',
        'Facility',
        'Issue',
        'KeyReport',
        'Market',
        'Metric',
        'Objective',
        'OrgGroup',
        'Person',
        'Policy',
        'Process',
        'Product',
        'ProductGroup',
        'Program',
        'Project',
        'Regulation',
        'Requirement',
        'Standard',
        'System',
        'Vendor',
        'Risk',
        'TechnologyEnvironment',
        'Threat',
      ],
      notMappable: ['Assessment', 'AssessmentTemplate', 'Evidence', 'Person'],
      scope: [
        'Metric', 'TechnologyEnvironment', 'AccessGroup', 'DataAsset',
        'Facility', 'KeyReport', 'Market', 'OrgGroup', 'Vendor', 'Process',
        'Product', 'ProductGroup', 'Project', 'System', 'AccountBalance',
      ],
    },
    risk_assessments: {
      models: ['RiskAssessment'],
      notMappable: ['RiskAssessment'],
    },
    workflows: {
      models: [
        'TaskGroup',
        'TaskGroupTask',
        'Workflow',
        'CycleTaskGroupObjectTask',
        'CycleTaskGroup',
      ],
      notMappable: [
        'Workflow',
        'TaskGroup',
        'TaskGroupTask',
        'CycleTaskGroupObjectTask',
        'CycleTaskGroup',
      ],
    },
  };

  function getModelsFromGroups(groups, groupNames) {
    let models = [];
    groupNames.forEach(function (groupName) {
      let groupModels = groups[groupName].items.map(function (item) {
        return item.value;
      });
      models = models.concat(groupModels);
    });
    return models;
  }

  Object.keys(modules).forEach(function (module) {
    allTypes = allTypes.concat(modules[module].models);
    notMappableModels = notMappableModels.concat(modules[module].notMappable);
  });

  const filtered = _.difference(allTypes, notMappableModels);

  const mappingRules = Object.freeze({
    AccessGroup: _.difference(filtered, ['AccessGroup', 'Standard',
      'Regulation']),
    AccountBalance: _.difference(filtered, ['Standard', 'Regulation']),
    Assessment: _.difference(filtered, ['Audit', 'Person', 'Program', 'Project',
      'Workflow', 'Assessment', 'Document']),
    AssessmentTemplate: [],
    Audit: _.difference(filtered, ['Audit', 'Person', 'Program', 'Project',
      'Workflow', 'Assessment', 'Document']),
    Contract: _.difference(filtered, ['Contract']),
    Control: filtered,
    CycleTaskGroupObjectTask: _.difference(filtered, ['Person',
      'Workflow', 'Assessment', 'Document']),
    DataAsset: _.difference(filtered, ['Standard', 'Regulation']),
    Evidence: [],
    Document: _.difference(filtered,
      ['Audit', 'Assessment', 'Document', 'Person', 'Workflow']),
    Facility: _.difference(filtered, ['Standard', 'Regulation']),
    Issue: _.difference(filtered, [
      'Audit', 'Person', 'Workflow', 'Assessment']),
    KeyReport: _.difference(filtered, ['Standard', 'Regulation']),
    Market: _.difference(filtered, ['Standard', 'Regulation']),
    Metric: _.difference(filtered, ['Standard', 'Regulation']),
    Objective: filtered,
    OrgGroup: _.difference(filtered, ['Standard', 'Regulation']),
    Person: [],
    Policy: _.difference(filtered, ['Policy']),
    Process: _.difference(filtered, ['Standard', 'Regulation']),
    Product: _.difference(filtered, ['Standard', 'Regulation']),
    ProductGroup: _.difference(filtered, ['Standard', 'Regulation']),
    Program: _.difference(allTypes,
      ['Program', 'Audit', 'RiskAssessment', 'Assessment', 'Person']
        .concat(modules.core.notMappable, modules.workflows.notMappable)),
    Project: _.difference(filtered, ['Standard', 'Regulation']),
    Regulation: _.difference(filtered, [...modules.core.scope, 'Regulation']),
    Risk: filtered,
    RiskAssessment: [],
    Requirement: filtered,
    Standard: _.difference(filtered, [...modules.core.scope, 'Standard']),
    System: _.difference(filtered, ['Standard', 'Regulation']),
    TaskGroup: _.difference(filtered, ['Audit', 'Person',
      'Workflow', 'Assessment', 'Document']),
    TechnologyEnvironment: _.difference(filtered, ['Standard', 'Regulation']),
    Threat: filtered,
    Vendor: _.difference(filtered, ['Standard', 'Regulation']),
    MultitypeSearch: _.difference(allTypes, ['CycleTaskGroup',
      'RiskAssessment']),
  });

  describe('getMappingTypes() method', function () {
    let EXPECTED_GROUPS = ['entities', 'scope', 'governance'];

    let types = allTypes.concat('MultitypeSearch');
    let modelsForTests = _.difference(types, [
      'TaskGroupTask',
      'CycleTaskGroup',
      'Workflow',
    ]);

    modelsForTests.forEach(function (type) {
      it('returns mappable types for ' + type, function () {
        let expectedModels = mappingRules[type];
        let result = Mappings.getMappingTypes(type);
        let resultGroups = Object.keys(result);
        let resultModels = getModelsFromGroups(result, EXPECTED_GROUPS);

        expect(EXPECTED_GROUPS).toEqual(resultGroups);
        expect(expectedModels.sort()).toEqual(resultModels.sort());
      });
    });
  });

  describe('isMappableType() method', function () {
    it('returns false for AssessmentTemplate and  any type', function () {
      let result = Mappings.isMappableType('AssessmentTemplate', 'Program');
      expect(result).toBe(false);
    });

    it('returns true for Program and Control', function () {
      let result = Mappings.isMappableType('Program', 'Control');
      expect(result).toBe(true);
    });
  });

  describe('allowedToMap() method', () => {
    beforeEach(() => {
      spyOn(Permission, 'is_allowed_for').and.returnValue(true);
    });

    it('checks that types are mappable', () => {
      spyOn(Mappings, 'isMappableType').and.returnValue(false);

      let result = Mappings.allowedToMap('SourceType', 'TargetType');

      expect(result).toBeFalsy();
      expect(Permission.is_allowed_for).not.toHaveBeenCalled();
    });

    it('checks permissions to update source', () => {
      spyOn(Mappings, 'isMappableType').and.returnValue(true);

      let result = Mappings.allowedToMap('DataAsset', 'AccessGroup');

      expect(result).toBeTruthy();
      expect(Permission.is_allowed_for)
        .toHaveBeenCalledWith('update', 'DataAsset');
      expect(Permission.is_allowed_for.calls.count()).toEqual(1);
    });

    it('checks permissions to update target', () => {
      spyOn(Mappings, 'isMappableType').and.returnValue(true);

      let source = new can.Map({type: 'DataAsset'});
      let target = new can.Map({type: 'AccessGroup'});
      let result = Mappings.allowedToMap(source, target);

      expect(result).toBeTruthy();
      expect(Permission.is_allowed_for.calls.count()).toEqual(2);
      expect(Permission.is_allowed_for.calls.argsFor(0))
        .toEqual(['update', source]);
      expect(Permission.is_allowed_for.calls.argsFor(1))
        .toEqual(['update', target]);
    });
  });

  describe('_prepareCorrectTypeFormat() method', function () {
    let cmsModel = {
      category: 'category',
      title_plural: 'title_plural',
      model_singular: 'model_singular',
    };
    let expectedResult = {
      category: 'category',
      name: 'title_plural',
      value: 'model_singular',
    };

    it('returns specified object', function () {
      let result;
      result = Mappings._prepareCorrectTypeFormat(cmsModel);
      expect(result).toEqual(expectedResult);
    });

    it('converts models plural title to a snake_case', function () {
      let result;
      let cmsModel1 = _.assign({}, cmsModel, {
        title_plural: 'Title Plural',
      });
      result = Mappings._prepareCorrectTypeFormat(cmsModel1);
      expect(result.plural).toEqual(expectedResult.plural);
    });
  });

  describe('addFormattedType() method', function () {
    let groups;
    let type = {
      category: 'category',
    };

    beforeEach(function () {
      groups = {
        governance: {
          items: [],
        },
        category: {
          items: [],
        },
      };
      spyOn(Mappings, '_prepareCorrectTypeFormat')
        .and.returnValue(type);
    });

    it('adds type to governance group if no group with category of this type',
      function () {
        groups.category = undefined;
        spyOn(Utils, 'getModelByType')
          .and.returnValue({
            title_singular: 'title_singular',
          });
        Mappings._addFormattedType('name', groups);
        expect(groups.governance.items[0]).toEqual(type);
      });

    it('adds type to group of category of this type if this group exist',
      function () {
        groups.governance = undefined;
        spyOn(Utils, 'getModelByType')
          .and.returnValue({
            title_singular: 'title_singular',
          });
        Mappings._addFormattedType('name', groups);
        expect(groups[type.category].items[0]).toEqual(type);
      });

    it('does nothing if cmsModel is not defined', function () {
      spyOn(Utils, 'getModelByType');
      Mappings._addFormattedType('name', groups);
      expect(groups.governance.items.length).toEqual(0);
      expect(groups[type.category].items.length).toEqual(0);
    });
    it('does nothing if singular title of cmsModel is not defined',
      function () {
        spyOn(Utils, 'getModelByType')
          .and.returnValue({});
        Mappings._addFormattedType('name', groups);
        expect(groups.governance.items.length).toEqual(0);
        expect(groups[type.category].items.length).toEqual(0);
      });
  });
});
