/*
  Copyright (C) 2019 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

describe('can.stache.helper.debugger', () => {
  let fakeOptions;
  let helper;

  beforeAll(() => {
    fakeOptions = {
      fn: jasmine.createSpy(),
    };

    helper = can.stache.getHelper('debugger').fn;
  });

  it('does not throw an error when called with more than one argument', () => {
    try {
      helper(1, 'foo', ['bar'], fakeOptions);
    } catch (ex) {
      fail('Helper threw an error: ' + ex.message);
    }
  });
});
