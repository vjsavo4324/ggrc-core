/*
  Copyright (C) 2019 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/
import Component from '../tree-item-attr';
import {getComponentVM} from '../../../../js_specs/spec_helpers';
import * as MarkdownUtils from '../../../plugins/utils/markdown-utils';

describe('tree-item-attr component', () => {
  let viewModel;

  beforeEach(() => {
    viewModel = getComponentVM(Component);
    viewModel.attr('instance', new can.Map());
  });

  it('returns an empty string if the attribute is missing', () => {
    viewModel.attr({name: 'does_not_exist'});

    let result = viewModel.getDefaultValue();
    expect(result).toEqual('');
  });

  describe('retrieving a "default" (non-date) attribute', () => {
    it('returns a correct value through the .attr() method', () => {
      viewModel.attr({
        name: 'slug',
        instance: {
          slug: 'DATAASSET-2',
        },
      });

      let result = viewModel.getDefaultValue();
      expect(result).toEqual('DATAASSET-2');
    });

    it('returns "true" string when boolean attr value is true', () => {
      viewModel.attr({
        name: 'archived',
        instance: {
          archived: true,
        },
      });

      let result = viewModel.getDefaultValue();
      expect(result).toEqual('true');
    });

    it('returns "false" string when boolean attr value is false', () => {
      viewModel.attr({
        name: 'archived',
        instance: {
          archived: false,
        },
      });

      let result = viewModel.getDefaultValue();
      expect(result).toEqual('false');
    });
  });

  describe('retrieving a date-like attribute', () => {
    it('returns a correctly formatted value through the .attr() method',
      () => {
        viewModel.attr({
          name: 'start_date',
          instance: {
            start_date: '1980-05-17',
          },
        });
        spyOn(viewModel.attr('instance'), 'attr').and.returnValue('2016-01-22');

        let result = viewModel.getDefaultValue();
        expect(viewModel.attr('instance').attr)
          .toHaveBeenCalledWith('start_date');
        expect(result).toEqual('01/22/2016');
      }
    );
  });

  describe('retrieving a rich text attribute', () => {
    it('returns a correctly formatted value through the .attr() method', () => {
      viewModel.attr({
        name: 'notes',
        instance: {
          notes: 'Notes',
        },
      });
      spyOn(viewModel.attr('instance'), 'attr')
        .and.returnValue('<p><strong>Example</strong></p><p>Notes</p>');

      let result = viewModel.getDefaultValue();
      expect(viewModel.attr('instance').attr).toHaveBeenCalledWith('notes');
      expect(result).toEqual('Example \n Notes');
    });

    describe('if isMarkdown is true', () => {
      it('returns a correctly formatted value through the .attr() method',
        () => {
          spyOn(viewModel, 'isMarkdown').and.returnValue(true);
          spyOn(MarkdownUtils, 'convertMarkdownToHtml')
            .and.returnValue('<strong>Example for markdown</strong>');
          viewModel.attr({
            name: 'notes',
            instance: {
              notes: 'some markdown notes',
            },
          });

          const result = viewModel.getDefaultValue();

          expect(MarkdownUtils.convertMarkdownToHtml)
            .toHaveBeenCalledWith('some markdown notes');
          expect(result).toEqual('Example for markdown');
        });
    });
  });
});
