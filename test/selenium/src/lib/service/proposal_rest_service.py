# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Services for create and manipulate Proposal objects via Rest."""
from dateutil import parser, tz

from lib import constants, url
from lib.constants import objects
from lib.service import rest_service
from lib.service.rest import query
from lib.utils import string_utils


class ProposalsService(rest_service.HelpRestService):
  """Class for Proposals business layer's services objects."""
  def __init__(self):
    super(ProposalsService, self).__init__(url.QUERY)

  def get_obj_proposals(self, obj):
    """Get and return object proposals according to obj type and id."""
    # double waiting for this rest method
    return rest_service.BaseRestService.get_items_from_resp(
        self.client.create_object(
            type=self.endpoint,
            object_name=objects.get_obj_type(objects.PROPOSALS),
            filters=query.Query.expression_get_obj_proposals(obj.type, obj.id),
            order_by=[
                {"name": "status", "desc": True},
                {"name": "created_at", "desc": True}]),
        timeout=constants.ux.TWO_MIN_USER_WAIT).get("values")

  def get_proposal_creation_date(self, obj, proposal):
    """Get proposal creation date."""
    proposals = self.get_obj_proposals(obj)
    prop_value = string_utils.escape_html(
        proposal.changes[0]["proposed_value"])
    try:
      actual_proposal = next(
          prop for prop in proposals
          if prop_value in prop["content"]["fields"]["description"])
    except StopIteration as exception:
      print proposals
      print prop_value
      raise exception
    return parser.parse(actual_proposal["created_at"]).replace(
        tzinfo=tz.tzutc())
