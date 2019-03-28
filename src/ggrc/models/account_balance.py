# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Module for AccountBalance object."""

from sqlalchemy import orm

from ggrc import db
from ggrc.access_control import roleable
from ggrc.models.comment import ScopedCommentable
from ggrc.models.deferred import deferred
from ggrc.models import mixins
from ggrc.fulltext import mixin as fulltext_mixin
from ggrc.models import object_document
from ggrc.models import object_person
from ggrc.models import reflection
from ggrc.models import relationship


class AccountBalance(
    mixins.CustomAttributable,
    object_person.Personable,
    roleable.Roleable,
    relationship.Relatable,
    object_document.PublicDocumentable,
    ScopedCommentable,
    mixins.TestPlanned,
    mixins.LastDeprecatedTimeboxed,
    mixins.base.ContextRBAC,
    mixins.ScopeObject,
    mixins.Folderable,
    fulltext_mixin.Indexed,
    db.Model,
):
  """Class representing AccountBalance model."""

  __tablename__ = "account_balances"

  infrastructure = deferred(db.Column(db.Boolean), "AccountBalance")
  version = deferred(db.Column(db.String), "AccountBalance")

  _api_attrs = reflection.ApiAttributes(
      "infrastructure",
      "version",
  )
  _fulltext_attrs = [
      "infrastructure",
      "version",
  ]
  _sanitize_html = ["version"]
  _aliases = {
      "documents_file": None,
  }

  @classmethod
  def indexed_query(cls):
    query = super(AccountBalance, cls).indexed_query()
    return query.options(
        orm.Load(cls).load_only(
            "id",
            "infrastructure",
            "version",
        )
    )
