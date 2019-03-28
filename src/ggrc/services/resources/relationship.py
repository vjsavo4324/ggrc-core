# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Custom Resource for Relationship that creates Snapshots when needed.

When Audit-Snapshottable Relationship is POSTed, a Snapshot should be created
instead.
"""

from werkzeug.exceptions import MethodNotAllowed

from ggrc.builder import json as json_builder
from ggrc import db
import ggrc.services.common
from ggrc.models.snapshot import Snapshot
from ggrc.models import relationship
from ggrc.models.mixins.with_readonly_access import WithReadOnlyAccess
from ggrc.login import get_current_user
from ggrc.utils import referenced_objects


class RelationshipResource(ggrc.services.common.Resource):
  """Custom Resource that transforms Relationships to Snapshots on un-json."""

  # pylint: disable=abstract-method

  @staticmethod
  def _validate_readonly_relationship(obj_with_readonly_access, obj2):
    # type: (WithReadOnlyAccess, Any) -> None
    """Validate if relationship change allowed to obj2

    Args:
      obj_with_readonly_access: object of type WithReadOnlyAccess
      obj2: another object which also can have type WithReadOnlyAccess
    """

    if not obj_with_readonly_access.can_change_relationship_with(obj2):
      raise MethodNotAllowed(
          description="The object is in a read-only mode and is "
                      "dedicated for SOX needs")

  @staticmethod
  def _validate_readonly_access(obj):
    """Ensure that relationship is allowed for read-only objects"""

    if not isinstance(obj, relationship.Relationship):
      # skip Snapshot objects
      return

    obj1 = referenced_objects.get(obj.source_type, obj.source_id)
    obj2 = referenced_objects.get(obj.destination_type, obj.destination_id)

    if isinstance(obj1, WithReadOnlyAccess):
      RelationshipResource._validate_readonly_relationship(obj1, obj2)

    if isinstance(obj2, WithReadOnlyAccess):
      RelationshipResource._validate_readonly_relationship(obj2, obj1)

  @staticmethod
  def _validate_readonly_access_on_post(objects):
    """Validate read-only access on POST"""

    for obj in objects:
      RelationshipResource._validate_readonly_access(obj)

  @staticmethod
  def _parse_snapshot_data(src):
    """Try to find parent-child pair from src.

    Args:
      src: source JSON from which a Relationship would have been created.

    Returns:
      (parent, child, is_snapshot):
          (source, destination, True) if source is a Parent and destination is
          a Snapshottable;
          (destination, source, True) if source is a Snapshottable and
          destination is a Parent;
          (None, None, False) otherwise.
    """
    from ggrc.snapshotter import rules as snapshot_rules
    parent, child = None, None
    if src["source"]["type"] in snapshot_rules.Types.parents:
      parent, child = src["source"], src["destination"]
    elif src["destination"]["type"] in snapshot_rules.Types.parents:
      parent, child = src["destination"], src["source"]

    is_snapshot = bool(parent) and child["type"] in snapshot_rules.Types.all
    return parent, child, is_snapshot

  def _get_model_instance(self, src=None):
    """For Parent and Snapshottable src and dst, create an empty Snapshot."""
    _, _, is_snapshot = self._parse_snapshot_data(src)

    if is_snapshot:
      obj = Snapshot()
      db.session.add(obj)
      return obj
    return super(RelationshipResource, self)._get_model_instance(src)

  def json_create(self, obj, src):
    """For Parent and Snapshottable src and dst, fill in the Snapshot obj."""
    parent, child, is_snapshot = self._parse_snapshot_data(src)

    if is_snapshot:
      snapshot_data = {
          "parent": parent,
          "child_type": child["type"],
          "child_id": child["id"],
          "update_revision": "new",
      }
      json_builder.create(obj, snapshot_data)
      obj.modified_by = get_current_user()
      obj.context = obj.parent.context
      relationship.Relationship(
          source=obj.parent,
          destination=obj,
      )
      return None

    return super(RelationshipResource, self).json_create(obj, src)
