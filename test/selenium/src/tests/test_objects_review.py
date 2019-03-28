# -*- coding: utf-8 -*-
# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Object review workflow tests."""
# pylint: disable=no-self-use
# pylint: disable=invalid-name
# pylint: disable=unused-argument
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=redefined-outer-name

import pytest

from lib import base, users
from lib.constants import roles
from lib.constants.element import ReviewStates
from lib.service import rest_service, webui_facade, rest_facade


class TestObjectsReview(base.Test):
  """Tests for objects review workflow."""

  @pytest.fixture()
  def program_with_assigned_reviewer(self):
    """Creates program with assigned review.
    Returns program and reviewer person."""
    reviewer = rest_facade.create_user_with_role(roles.CREATOR)
    users.set_current_user(rest_facade.create_user_with_role(roles.CREATOR))
    program_with_review = rest_service.ReviewService().request_review(
        rest_facade.create_program(), reviewer)
    return {"program": program_with_review,
            "reviewer": reviewer}

  @pytest.mark.smoke_tests
  def test_request_obj_review(self, selenium):
    """Confirm reviewer is displayed on Program Info panel."""
    reviewer = rest_facade.create_user_with_role(roles.CREATOR)
    users.set_current_user(rest_facade.create_user_with_role(roles.CREATOR))
    program = rest_facade.create_program()
    webui_facade.submit_obj_for_review(selenium, program, reviewer.email)
    actual_program = webui_facade.get_object(selenium, program)
    program.update_attrs(review={
        "status": ReviewStates.UNREVIEWED,
        "reviewers": [reviewer.email],
        "last_reviewed_by": ""})
    self.general_equal_assert(program.repr_ui(), actual_program)

  @pytest.mark.smoke_tests
  def test_obj_mark_reviewed(self, selenium, program_with_assigned_reviewer):
    """Confirm Reviewer with READ rights for an object
    able to Review an object."""
    expected_program = program_with_assigned_reviewer["program"]
    reviewer = program_with_assigned_reviewer["reviewer"]
    users.set_current_user(reviewer)
    webui_facade.approve_obj_review(selenium, expected_program)
    expected_program.update_attrs(review={
        "status": ReviewStates.REVIEWED,
        "reviewers": [reviewer.email],
        "last_reviewed_by": "Last reviewed by\n" + reviewer.email + "\non " +
                            rest_facade.get_last_review_date(expected_program)}
    )
    actual_program = webui_facade.get_object(selenium, expected_program)
    self.general_equal_assert(expected_program.repr_ui(), actual_program)
