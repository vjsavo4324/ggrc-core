# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Risks/Threats page smoke tests."""
# pylint: disable=no-self-use
# pylint: disable=too-few-public-methods

import pytest

from lib import base, users
from lib.entities import entities_factory
from lib.service import webui_service, rest_facade


class TestRiskThreatPage(base.Test):
  """Tests threat/risk page, part of smoke tests, section 8."""

  @pytest.mark.smoke_tests
  def test_create_risk(self, selenium):
    """Tests risk creation via UI."""
    risk = entities_factory.RisksFactory().create()
    actual_risk = webui_service.RisksService(
        selenium).create_obj_and_get_obj(risk)
    rest_risk = rest_facade.get_obj(actual_risk)
    risk.update_attrs(
        created_at=rest_risk.created_at,
        updated_at=rest_risk.updated_at,
        modified_by=users.current_user(),
        slug=rest_risk.slug,
        url=rest_risk.url).repr_ui()
    self.general_equal_assert(risk, actual_risk, "custom_attributes")
