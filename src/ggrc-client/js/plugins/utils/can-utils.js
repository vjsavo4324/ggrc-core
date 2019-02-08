/*
  Copyright (C) 2019 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import Map from 'can-map/can-map';
import isFunction from 'can-util/js/is-function/is-function';

const isObserveLike = (obj) => {
  return obj instanceof Map || obj && !!obj._get;
};

const isArrayLike = (obj) => {
  return obj && obj.splice && typeof obj.length === 'number';
};

const resolve = (value) => {
  if (isObserveLike(value) && isArrayLike(value) && value.attr('length')) {
    return value;
  } else if (isFunction(value)) {
    return value();
  } else {
    return value;
  }
};

export {
  resolve,
};
