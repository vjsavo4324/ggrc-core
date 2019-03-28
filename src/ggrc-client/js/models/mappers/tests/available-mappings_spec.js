/*
  Copyright (C) 2019 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import Mappings from '../mappings';

describe('Mappings', () => {
  const types = Mappings.getAllowedToMapModels('MultitypeSearch');

  let modules = {
    core: [
      'AccessGroup',
      'AccountBalance',
      'Contract',
      'Control',
      'DataAsset',
      'Facility',
      'Issue',
      'KeyReport',
      'Market',
      'Metric',
      'Objective',
      'OrgGroup',
      'Policy',
      'Process',
      'Product',
      'ProductGroup',
      'Project',
      'Regulation',
      'Requirement',
      'Risk',
      'Standard',
      'System',
      'TechnologyEnvironment',
      'Threat',
      'Vendor',
    ],
    audit: [
      'Evidence',
      'Assessment',
      'AssessmentTemplate',
      'Audit',
    ],
    workflow: [
      'TaskGroup',
      'Workflow',
    ],
  };

  const coreObjectsRules = _.concat(modules.core, modules.workflow,
    ['Assessment', 'Audit', 'Document', 'Person', 'Program']);
  const snapshotableObjects = _.difference(modules.core, ['Project']);

  const mappingRules = {
    AccessGroup: _.difference(coreObjectsRules, ['AccessGroup']),
    AccountBalance: coreObjectsRules,
    Assessment: [...snapshotableObjects, 'Evidence', 'Audit', 'Person'],
    AssessmentTemplate: ['Audit'],
    Audit: [...snapshotableObjects, 'Evidence', 'Assessment',
      'AssessmentTemplate', 'Person', 'Program'],
    Contract: _.difference(coreObjectsRules, ['Contract']),
    Control: coreObjectsRules,
    CycleTaskGroupObjectTask: [...modules.core, 'Audit', 'Person', 'Program',
      'Workflow'],
    DataAsset: coreObjectsRules,
    Document: [...modules.core, 'Person', 'Program'],
    Evidence: ['Assessment', 'Audit', 'Person'],
    Facility: coreObjectsRules,
    Issue: coreObjectsRules,
    KeyReport: coreObjectsRules,
    Market: coreObjectsRules,
    Metric: coreObjectsRules,
    Objective: coreObjectsRules,
    OrgGroup: coreObjectsRules,
    Person: [...modules.core, 'Assessment', 'Audit', 'CycleTaskGroupObjectTask',
      'Evidence', 'Document', 'Program', 'TaskGroupTask', 'Workflow'],
    Policy: _.difference(coreObjectsRules, ['Policy']),
    Process: coreObjectsRules,
    Product: coreObjectsRules,
    ProductGroup: coreObjectsRules,
    Program:
      [...modules.core, ...modules.workflow, 'Audit', 'Document', 'Person'],
    Project: coreObjectsRules,
    Regulation: _.difference(coreObjectsRules, ['Regulation']),
    Requirement: coreObjectsRules,
    Risk: coreObjectsRules,
    Standard: _.difference(coreObjectsRules, ['Standard']),
    System: coreObjectsRules,
    TaskGroup: [...modules.core, 'Program', 'Workflow'],
    TaskGroupTask: ['Person', 'Workflow'],
    TechnologyEnvironment: coreObjectsRules,
    Threat: coreObjectsRules,
    Vendor: coreObjectsRules,
    Workflow: ['Person', 'TaskGroup', 'TaskGroupTask'],
  };

  describe('getAvailableMappings() method', () => {
    Object.keys(types).forEach(function (type) {
      it('returns available types for ' + type, function () {
        let expectedModels = mappingRules[type];
        let result = Mappings.getAvailableMappings(type);
        let resultModels = Object.keys(result);

        expect(expectedModels.sort()).toEqual(resultModels.sort());
      });
    });
  });
});
