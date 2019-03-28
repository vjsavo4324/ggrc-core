# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Contains a WithReadOnlyAccess mixin.

It allows to mark objects as read-only
"""

from ggrc import db
from ggrc.models import reflection


class WithReadOnlyAccess(object):
  """Mixin for models which can be marked as read-only"""
  # pylint: disable=too-few-public-methods

  _read_only_model_relationships = (
      'Document'
  )

  readonly = db.Column(db.Boolean, nullable=False, default=False)

  _api_attrs = reflection.ApiAttributes(
      reflection.Attribute("readonly", create=False, update=False),
  )

  _aliases = {
      "readonly": {
          "display_name": "Read-only",
          "mandatory": False,
          "hidden": True,
      },
  }

  def can_change_relationship_with(self, obj):
    """Check whether relationship from self to obj1 can be changed

    This function doesn't expect that another obj also has type
    WithReadOnlyAccess. In this case can_change_relationship_with() of
    another object have to be called also to ensure that relationship is
    not read-only. Final read-only flag can be calculated
    using the following expression:
      obj1.can_change_relationship_with(obj2) and \
      obj2.can_change_relationship_with(obj1)
    """

    if not self.readonly:
      return True

    return obj.__class__.__name__ not in self._read_only_model_relationships
