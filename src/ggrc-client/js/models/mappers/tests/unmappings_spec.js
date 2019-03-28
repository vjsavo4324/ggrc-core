/*
 Copyright (C) 2019 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

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

  Object.keys(modules).forEach(function (module) {
    allTypes = allTypes.concat(modules[module].models);
    notMappableModels = notMappableModels.concat(modules[module].notMappable);
  });

  const filtered = _.difference(allTypes, notMappableModels);

  const unmappingRules = Object.freeze({
    AccessGroup: _.difference(filtered, ['AccessGroup', 'Audit', 'Standard',
      'Regulation']),
    AccountBalance: _.difference(filtered, ['Audit', 'Standard', 'Regulation']),
    Assessment: _.difference(filtered, ['Audit', 'Person', 'Program', 'Project',
      'Workflow', 'Assessment', 'Document']),
    AssessmentTemplate: [],
    Audit: ['Issue'],
    Contract: _.difference(filtered, ['Audit', 'Contract']),
    Control: _.difference(filtered, ['Audit']),
    CycleTaskGroupObjectTask: _.difference(filtered, ['Person',
      'Workflow', 'Assessment', 'Document']),
    DataAsset: _.difference(filtered, ['Audit', 'Standard', 'Regulation']),
    Evidence: [],
    Document: _.difference(filtered,
      ['Audit', 'Assessment', 'Document', 'Person', 'Workflow']),
    Facility: _.difference(filtered, ['Audit', 'Standard', 'Regulation']),
    Issue: _.difference(allTypes,
      ['RiskAssessment', 'Person', 'AssessmentTemplate', 'Evidence']
        .concat(modules.workflows.notMappable)),
    KeyReport: _.difference(filtered, ['Audit', 'Standard', 'Regulation']),
    Market: _.difference(filtered, ['Audit', 'Standard', 'Regulation']),
    Metric: _.difference(filtered, ['Audit', 'Standard', 'Regulation']),
    Objective: _.difference(filtered, ['Audit']),
    OrgGroup: _.difference(filtered, ['Audit', 'Standard', 'Regulation']),
    Person: [],
    Policy: _.difference(filtered, ['Audit', 'Policy']),
    Process: _.difference(filtered, ['Audit', 'Standard', 'Regulation']),
    Product: _.difference(filtered, ['Audit', 'Standard', 'Regulation']),
    ProductGroup: _.difference(filtered, ['Audit', 'Standard', 'Regulation']),
    Program: _.difference(allTypes,
      ['Program', 'Audit', 'RiskAssessment', 'Assessment', 'Person']
        .concat(modules.core.notMappable, modules.workflows.notMappable)),
    Project: _.difference(filtered, ['Audit', 'Standard', 'Regulation']),
    Regulation: _.difference(filtered,
      [...modules.core.scope, 'Audit', 'Regulation']),
    Risk: _.difference(filtered, ['Audit']),
    RiskAssessment: [],
    Requirement: _.difference(filtered, ['Audit']),
    Standard: _.difference(filtered,
      [...modules.core.scope, 'Audit', 'Standard']),
    System: _.difference(filtered, ['Audit', 'Standard', 'Regulation']),
    TaskGroup: _.difference(filtered, ['Audit', 'Person',
      'Workflow', 'Assessment', 'Document']),
    TechnologyEnvironment: _.difference(filtered,
      ['Audit', 'Standard', 'Regulation']),
    Threat: _.difference(filtered, ['Audit']),
    Vendor: _.difference(filtered, ['Audit', 'Standard', 'Regulation']),
  });

  describe('allowedToUnmap() method', () => {
    beforeEach(() => {
      spyOn(Permission, 'is_allowed_for').and.returnValue(true);
    });

    it('checks that types are mappable', () => {
      spyOn(Mappings, 'getAllowedToUnmapModels').and.returnValue({
        Control: {},
      });

      let result = Mappings.allowedToUnmap('SourceType', 'TargetType');

      expect(result).toBeFalsy();
      expect(Permission.is_allowed_for).not.toHaveBeenCalled();
    });

    it('checks permissions to update source', () => {
      spyOn(Mappings, 'getAllowedToUnmapModels').and.returnValue({
        AccessGroup: {},
      });

      let result = Mappings.allowedToUnmap('DataAsset', 'AccessGroup');

      expect(result).toBeTruthy();
      expect(Permission.is_allowed_for)
        .toHaveBeenCalledWith('update', 'DataAsset');
      expect(Permission.is_allowed_for.calls.count()).toEqual(1);
    });

    it('checks permissions to update target', () => {
      spyOn(Mappings, 'getAllowedToUnmapModels').and.returnValue({
        AccessGroup: {},
      });

      let source = new can.Map({type: 'DataAsset'});
      let target = new can.Map({type: 'AccessGroup'});
      let result = Mappings.allowedToUnmap(source, target);

      expect(result).toBeTruthy();
      expect(Permission.is_allowed_for.calls.count()).toEqual(2);
      expect(Permission.is_allowed_for.calls.argsFor(0))
        .toEqual(['update', source]);
      expect(Permission.is_allowed_for.calls.argsFor(1))
        .toEqual(['update', target]);
    });
  });

  describe('getAllowedToUnmapModels() method', () => {
    let modelsForTests = _.difference(allTypes, [
      'TaskGroupTask',
      'CycleTaskGroup',
      'Workflow',
    ]);

    modelsForTests.forEach(function (type) {
      it('returns mappable types for ' + type, function () {
        let expectedModels = unmappingRules[type];
        let result = Mappings.getAllowedToUnmapModels(type);
        let resultModels = _.keys(result);

        expect(expectedModels.sort()).toEqual(resultModels.sort());
      });
    });
  });
});
