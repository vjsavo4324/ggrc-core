# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Module for Relationship model and related classes."""

import logging

import collections
import sqlalchemy as sa
from sqlalchemy import or_, and_
from sqlalchemy.ext.declarative import declared_attr

from ggrc import db
from ggrc.login import is_external_app_user
from ggrc.models.mixins import base
from ggrc.models.mixins import Base
from ggrc.models import reflection
from ggrc.models.exceptions import ValidationError

logger = logging.getLogger(__name__)


class Relationship(base.ContextRBAC, Base, db.Model):
  """Relationship model."""
  __tablename__ = 'relationships'
  source_id = db.Column(db.Integer, nullable=False)
  source_type = db.Column(db.String, nullable=False)
  destination_id = db.Column(db.Integer, nullable=False)
  destination_type = db.Column(db.String, nullable=False)
  parent_id = db.Column(
      db.Integer,
      db.ForeignKey('relationships.id', ondelete='SET NULL'),
      nullable=True,
  )
  parent = db.relationship(
      lambda: Relationship,
      remote_side=lambda: Relationship.id
  )
  automapping_id = db.Column(
      db.Integer,
      db.ForeignKey('automappings.id', ondelete='CASCADE'),
      nullable=True,
  )
  is_external = db.Column(db.Boolean, nullable=False, default=False)

  def get_related_for(self, object_type):
    """Return related object for sent type."""
    if object_type == self.source_type:
      return self.destination
    if object_type == self.destination_type:
      return self.source

  @property
  def source_attr(self):
    return '{0}_source'.format(self.source_type)

  @property
  def source(self):
    """Source getter."""
    if not hasattr(self, self.source_attr):
      logger.warning(
          "Relationship source attr '%s' does not exist. "
          "This indicates invalid data in our database!",
          self.source_attr
      )
      return None
    return getattr(self, self.source_attr)

  @source.setter
  def source(self, value):
    self.source_id = getattr(value, 'id', None)
    self.source_type = getattr(value, 'type', None)
    self.validate_relatable_type("source", value)
    return setattr(self, self.source_attr, value)

  @property
  def destination_attr(self):
    return '{0}_destination'.format(self.destination_type)

  @property
  def destination(self):
    """Destination getter."""
    if not hasattr(self, self.destination_attr):
      logger.warning(
          "Relationship destination attr '%s' does not exist. "
          "This indicates invalid data in our database!",
          self.destination_attr
      )
      return None
    return getattr(self, self.destination_attr)

  @destination.setter
  def destination(self, value):
    self.destination_id = getattr(value, 'id', None)
    self.destination_type = getattr(value, 'type', None)
    self.validate_relatable_type("destination", value)
    return setattr(self, self.destination_attr, value)

  @classmethod
  def find_related(cls, object1, object2):
    return cls.get_related_query(object1, object2).first()

  @classmethod
  def get_related_query(cls, object1, object2):
    def predicate(src, dst):
      return and_(
          Relationship.source_type == src.type,
          or_(Relationship.source_id == src.id, src.id == None),  # noqa
          Relationship.destination_type == dst.type,
          or_(Relationship.destination_id == dst.id, dst.id == None),  # noqa
      )
    return Relationship.query.filter(
        or_(predicate(object1, object2), predicate(object2, object1))
    )

  @staticmethod
  def _extra_table_args(cls):
    return (
        db.UniqueConstraint(
            'source_id', 'source_type', 'destination_id', 'destination_type'),
        db.Index(
            'ix_relationships_source',
            'source_type', 'source_id'),
        db.Index(
            'ix_relationships_destination',
            'destination_type', 'destination_id'),
    )

  _api_attrs = reflection.ApiAttributes(
      'source',
      'destination',
      reflection.Attribute(
          'is_external', create=True, update=False, read=True),
  )

  def _display_name(self):
    return "{}:{} <-> {}:{}".format(self.source_type, self.source_id,
                                    self.destination_type, self.destination_id)

  def validate_relatable_type(self, field, value):
    if value is None:
      raise ValidationError(u"{}.{} can't be None."
                            .format(self.__class__.__name__, field))
    if not isinstance(value, Relatable):
      raise ValidationError(u"You are trying to create relationship with not "
                            u"Relatable type: {}".format(value.type))
    tgt_type = self.source_type
    tgt_id = self.source_id
    self.validate_relation_by_type(self.source_type, self.destination_type)

    if field == "source":
      tgt_type = self.destination_type
      tgt_id = self.destination_id
    if value and getattr(value, "type") == "Snapshot":
      if not tgt_type:
        return
      if value.child_type == tgt_type and value.child_id == tgt_id:
        raise ValidationError(
            u"Invalid source-destination types pair for {}: "
            u"source_type={!r}, destination_type={!r}"
            .format(self.type, self.source_type, self.destination_type)
        )
    # else check if the opposite is a Snapshot
    elif tgt_type == "Snapshot":
      from ggrc.models import Snapshot
      snapshot = db.session.query(Snapshot).get(tgt_id)
      if snapshot.child_type == value.type and snapshot.child_id == value.id:
        raise ValidationError(
            u"Invalid source-destination types pair for {}: "
            u"source_type={!r}, destination_type={!r}"
            .format(self.type, self.source_type, self.destination_type)
        )

  @staticmethod
  def _check_relation_types_group(type1, type2, group1, group2):
    """Checks if 2 types belong to 2 groups

    Args:
      type1: name of model 1
      type2: name of model 2
      group1: Collection of model names which belong to group 1
      group1: Collection of model names which belong to group 2
    Return:
      True if types belong to different groups, else False
    """

    if (type1 in group1 and type2 in group2) or (type2 in group1 and
                                                 type1 in group2):
      return True

    return False

  # pylint:disable=unused-argument
  @classmethod
  def validate_delete(cls, mapper, connection, target):
    """Validates is delete of Relationship is allowed."""
    cls.validate_relation_by_type(target.source_type,
                                  target.destination_type)

  @classmethod
  def validate_relation_by_type(cls, source_type, destination_type):
    """Checks if a mapping is allowed between given types."""
    if is_external_app_user():
      # external users can map and unmap scoping objects
      return

    from ggrc.models import all_models
    scoping_models_names = all_models.get_scope_model_names()

    # Check Regulation and Standard
    if cls._check_relation_types_group(source_type, destination_type,
                                       scoping_models_names,
                                       ("Regulation", "Standard")):
      raise ValidationError(
          u"You do not have the necessary permissions to map and unmap "
          u"scoping objects to directives in this application. Please "
          u"contact your administrator if you have any questions.")

    # Check Control
    control_external_only_mappings = set(scoping_models_names)
    control_external_only_mappings.update(("Regulation", "Standard"))
    if cls._check_relation_types_group(source_type, destination_type,
                                       control_external_only_mappings,
                                       ("Control", )):
      raise ValidationError(
          u"You do not have the necessary permissions to map and unmap "
          u"controls to scoping objects, standards and regulations in this "
          u"application. Please contact your administrator "
          u"if you have any questions.")


class Relatable(object):
  """Mixin adding Relationship functionality to an object"""

  @declared_attr
  def related_sources(cls):  # pylint: disable=no-self-argument
    current_type = cls.__name__

    joinstr = (
        "and_("
        "foreign(remote(Relationship.destination_id)) == {type}.id,"
        "Relationship.destination_type == '{type}'"
        ")"
        .format(type=current_type)
    )

    # Since we have some kind of generic relationship here, it is needed
    # to provide custom joinstr for backref. If default, all models having
    # this mixin will be queried, which in turn produce large number of
    # queries returning nothing and one query returning object.
    backref_joinstr = (
        "remote({type}.id) == foreign(Relationship.destination_id)"
        .format(type=current_type)
    )

    return db.relationship(
        "Relationship",
        primaryjoin=joinstr,
        backref=sa.orm.backref(
            "{}_destination".format(current_type),
            primaryjoin=backref_joinstr,
        ),
        cascade="all, delete-orphan"
    )

  @declared_attr
  def related_destinations(cls):  # pylint: disable=no-self-argument
    current_type = cls.__name__

    joinstr = (
        "and_("
        "foreign(remote(Relationship.source_id)) == {type}.id,"
        "Relationship.source_type == '{type}'"
        ")"
        .format(type=current_type)
    )

    # Since we have some kind of generic relationship here, it is needed
    # to provide custom joinstr for backref. If default, all models having
    # this mixin will be queried, which in turn produce large number of
    # queries returning nothing and one query returning object.
    backref_joinstr = (
        "remote({type}.id) == foreign(Relationship.source_id)"
        .format(type=current_type)
    )

    return db.relationship(
        "Relationship",
        primaryjoin=joinstr,
        backref=sa.orm.backref(
            "{}_source".format(current_type),
            primaryjoin=backref_joinstr,
        ),
        cascade="all, delete-orphan"
    )

  def related_objects(self, _types=None):
    """Returns all or a subset of related objects of certain types.

    If types is specified, only return objects of selected types

    Args:
      _types: A set of object types
    Returns:
      A set (or subset if _types is specified) of related objects.
    """
    # pylint: disable=not-an-iterable
    source_objs = [obj.source for obj in self.related_sources
                   if obj.source is not None]
    dest_objs = [obj.destination for obj in self.related_destinations
                 if obj.destination is not None]
    related = source_objs + dest_objs

    if _types:
      return {obj for obj in related if obj and obj.type in _types}
    return set(related)

  _include_links = []

  @classmethod
  def eager_query(cls):
    from sqlalchemy import orm

    query = super(Relatable, cls).eager_query()
    return cls.eager_inclusions(query, Relatable._include_links).options(
        orm.subqueryload('related_sources'),
        orm.subqueryload('related_destinations'))


class Stub(collections.namedtuple("Stub", ["type", "id"])):
  """Minimal object representation."""

  @classmethod
  def from_source(cls, relationship):
    return Stub(relationship.source_type, relationship.source_id)

  @classmethod
  def from_destination(cls, relationship):
    return Stub(relationship.destination_type, relationship.destination_id)


class RelationshipsCache(object):
  """Cache of related objects"""
  # pylint: disable=too-few-public-methods

  def __init__(self):
    self.cache = collections.defaultdict(set)

  def populate_cache(self, stubs):
    """Fetch all mappings for objects in stubs, cache them in self.cache."""
    # Union is here to convince mysql to use two separate indices and
    # merge te results. Just using `or` results in a full-table scan
    # Manual column list avoids loading the full object which would also try to
    # load related objects
    cols = db.session.query(
        Relationship.source_type, Relationship.source_id,
        Relationship.destination_type, Relationship.destination_id)
    relationships = cols.filter(
        sa.tuple_(
            Relationship.source_type,
            Relationship.source_id
        ).in_(
            [(s.type, s.id) for s in stubs]
        )
    ).union_all(
        cols.filter(
            sa.tuple_(
                Relationship.destination_type,
                Relationship.destination_id
            ).in_(
                [(s.type, s.id) for s in stubs]
            )
        )
    ).all()
    for (src_type, src_id, dst_type, dst_id) in relationships:
      src = Stub(src_type, src_id)
      dst = Stub(dst_type, dst_id)
      # only store a neighbor if we queried for it since this way we know
      # we'll be storing complete neighborhood by the end of the loop
      if src in stubs:
        self.cache[src].add(dst)
      if dst in stubs:
        self.cache[dst].add(src)
