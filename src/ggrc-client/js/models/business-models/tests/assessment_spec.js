/*
  Copyright (C) 2019 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import Assessment from '../assessment';
import Program from '../program';
import Audit from '../audit';
import * as aclUtils from '../../../plugins/utils/acl-utils';
import {makeFakeInstance} from '../../../../js_specs/spec_helpers';
import Context from '../../service-models/context';
import * as modelsUtils from '../../../plugins/utils/models-utils';
import {REFRESH_MAPPING} from '../../../events/eventTypes';

describe('Assessment model', function () {
  'use strict';

  describe('before_create() method', function () {
    let assessment;
    let audit;
    let auditWithoutContext;
    let context;
    let program;

    beforeEach(function () {
      assessment = makeFakeInstance({model: Assessment})();
      context = makeFakeInstance({model: Context})({id: 42});
      program = makeFakeInstance({model: Program})({id: 54});
      const fakeAuditCreator = makeFakeInstance({model: Audit});
      audit = fakeAuditCreator({context, program});
      auditWithoutContext = fakeAuditCreator({program});
    });

    it('sets the program and context properties', function () {
      assessment.attr('audit', audit);
      assessment.before_create();
      expect(assessment.context.id).toEqual(context.id);
    });

    it('throws an error if audit is not defined', function () {
      expect(function () {
        assessment.before_create();
      }).toThrow(new Error('Cannot save assessment, audit not set.'));
    });

    it('throws an error if audit program/context are not defined', function () {
      assessment.attr('audit', auditWithoutContext);
      expect(function () {
        assessment.before_create();
      }).toThrow(new Error(
        'Cannot save assessment, audit context not set.'));
    });
    it('sets empty string to design property', function () {
      assessment.attr('audit', audit);
      assessment.attr('design', undefined);
      assessment.before_create();
      expect(assessment.attr('design')).toEqual('');
    });
    it('sets empty string to operationally property', function () {
      assessment.attr('audit', audit);
      assessment.attr('operationally', undefined);
      assessment.before_create();
      expect(assessment.attr('operationally')).toEqual('');
    });
  });

  describe('_transformBackupProperty() method', function () {
    let assessment;

    beforeEach(function () {
      assessment = makeFakeInstance({model: Assessment})();
    });
    it('does nothing if no backup of instance', function () {
      assessment.attr('name', '');
      assessment._transformBackupProperty(['name']);
      expect(assessment.attr('name')).toEqual('');
    });
    it('transforms backups property if it is falsy in instance and in backup' +
    'but not equal', function () {
      assessment.attr('name', '');
      assessment.backup();
      assessment._backupStore().name = null;
      assessment._transformBackupProperty(['name']);
      expect(assessment._backupStore().name).toEqual('');
    });
    it('updates validate_assessor in backup if it is define in instance',
      function () {
        assessment.backup();
        assessment.attr('validate_assessor', true);
        assessment._backupStore().validate_assessor = undefined;
        assessment._transformBackupProperty(['name']);
        expect(assessment._backupStore().validate_assessor).toEqual(true);
      });
    it('updates validate_creator in backup if it is define in instance',
      function () {
        assessment.backup();
        assessment.attr('validate_creator', true);
        assessment._backupStore().validate_creator = undefined;
        assessment._transformBackupProperty(['name']);
        expect(assessment._backupStore().validate_creator).toEqual(true);
      });
  });
  describe('isDirty() method', function () {
    let assessment;

    beforeEach(function () {
      assessment = makeFakeInstance({model: Assessment})();
      spyOn(assessment, '_transformBackupProperty')
        .and.callThrough();
    });
    it('calls _transformBackupProperty() with specified arguments',
      function () {
        assessment.isDirty();
        expect(assessment._transformBackupProperty)
          .toHaveBeenCalledWith(['design', 'operationally']);
      });
    it('returns result of inherited function, true if instance is dirty',
      function () {
        let result;
        assessment.attr('name', 'assessment1');
        assessment.backup();
        assessment.attr('name', 'assessment1.1');
        result = assessment.isDirty();
        expect(result).toEqual(true);
      });
    it('returns result of inherited function, false if instance is not dirty',
      function () {
        let result;
        assessment.attr('name', 'assessment1');
        assessment.backup();
        result = assessment.isDirty();
        expect(result).toEqual(false);
      });
  });

  describe('model() method', function () {
    it('does not update backup if backup was not created', function () {
      spyOn(_, 'assign');
      Assessment.model({data: 'test'}, makeFakeInstance({
        model: Assessment,
      })());
      expect(_.assign).not.toHaveBeenCalled();
    });

    it('updates backup if backup was created', function () {
      let model = makeFakeInstance({model: Assessment})();
      model.backup();
      Assessment.model({data: 'test'}, model);
      expect(model._backupStore().data).toBe('test');
    });
  });

  describe('form_preload() method', function () {
    beforeEach(() => {
      spyOn(modelsUtils, 'getInstance').and.returnValue(GGRC.current_user);
    });

    function checkAcRoles(model, roleId, peopleIds) {
      const res = can.makeArray(model.access_control_list).filter((acl) => {
        return acl.ac_role_id === roleId;
      }).map((acl) => {
        return acl.person.id;
      }).sort();
      expect(res).toEqual(peopleIds);
    }

    it('populates access control roles based on audit roles', function () {
      let model = makeFakeInstance({model: Assessment})();
      spyOn(model, 'before_create');
      spyOn(aclUtils, 'getRole').and.returnValues(
        {id: 10, name: 'Creators', object_type: 'Assessment'},
        {id: 11, name: 'Assignees', object_type: 'Assessment'},
        {id: 11, name: 'Assignees', object_type: 'Assessment'},
        {id: 11, name: 'Assignees', object_type: 'Assessment'},
        {id: 11, name: 'Assignees', object_type: 'Assessment'},
        {id: 12, name: 'Verifiers', object_type: 'Assessment'},
        {id: 12, name: 'Verifiers', object_type: 'Assessment'},
      );

      // Mock out the findRoles function
      model.attr('audit', {
        findRoles: (name) => {
          const roles = {
            Auditors: [
              {person: {id: 10, type: 'Person'}},
              {person: {id: 20, type: 'Person'}},
            ],
            'Audit Captains': [
              {person: {id: 20, type: 'Person'}},
              {person: {id: 30, type: 'Person'}},
              {person: {id: 40, type: 'Person'}},
              {person: {id: 50, type: 'Person'}},
            ],
          };
          return roles[name];
        },
      });
      model.form_preload(true);
      // Expect 7 new access_control_roles to be created
      expect(model.access_control_list.length).toBe(7);
      checkAcRoles(model, 10, [1]);
      checkAcRoles(model, 12, [10, 20]);
      checkAcRoles(model, 11, [20, 30, 40, 50]);
    });
    it('defaults correctly when auditors/audit captains are undefined',
      function () {
        let model = makeFakeInstance({model: Assessment})();
        spyOn(model, 'before_create');
        spyOn(aclUtils, 'getRole').and.returnValues(
          {id: 10, name: 'Creators', object_type: 'Assessment'},
          {id: 11, name: 'Assignees', object_type: 'Assessment'},
        );
        // Mock out the findRoles function
        model.attr('audit', {
          findRoles: (name) => {
            const roles = {
              Auditors: [],
              'Audit Captains': [],
            };
            return roles[name];
          },
        });
        model.form_preload(true);
        // Expect 7 new access_control_roles to be created
        expect(model.access_control_list.length).toBe(2);
        checkAcRoles(model, 10, [1]);
        checkAcRoles(model, 11, [1]);
        checkAcRoles(model, 12, []);
      });
  });

  describe('getRelatedObjects() method', () => {
    beforeEach(() => {
      spyOn($, 'get').and.returnValue($.Deferred().resolve({
        Audit: {
          title: 'FooBar',
        },
      }));
    });

    it('adds an audit title', (done) => {
      const model = makeFakeInstance({model: Assessment})({
        audit: {id: 123},
      });

      model.getRelatedObjects().then(() => {
        expect(model.attr('audit.title')).toBe('FooBar');
        done();
      });
    });
  });

  describe('handler for REFRESH_MAPPING event', () => {
    let instance;

    beforeEach(() => {
      instance = makeFakeInstance({model: Assessment})();
    });

    it('calls refresh of instance if it is in read mode status', () => {
      spyOn(instance, 'refresh');
      Assessment.readModeStatuses.forEach((status) => {
        instance.attr('status', status);

        instance.dispatch(REFRESH_MAPPING);
      });

      expect(instance.refresh)
        .toHaveBeenCalledTimes(Assessment.readModeStatuses.length);
    });

    it('does not call refresh of instance if it is in edit mode status', () => {
      spyOn(instance, 'refresh');
      Assessment.editModeStatuses.forEach((status) => {
        instance.attr('status', status);

        instance.dispatch(REFRESH_MAPPING);
      });

      expect(instance.refresh).not.toHaveBeenCalled();
    });
  });
});
