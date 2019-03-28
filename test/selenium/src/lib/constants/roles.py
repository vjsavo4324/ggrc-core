# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Constants for roles."""
from lib import url
from lib.decorator import lazy_property, memoize
from lib.service.rest.client import RestClient


# global roles
NO_ROLE = "No Role"
NO_ROLE_UI = "(Inactive user)"
ADMIN = "Admin"
CREATOR = "Creator"
READER = "Reader"
EDITOR = "Editor"
ADMINISTRATOR = "Administrator"
GLOBAL_ROLES = (CREATOR, EDITOR, ADMINISTRATOR)
# assessment roles
ASSIGNEES = "Assignees"
VERIFIERS = "Verifiers"
# program roles
PROGRAM_EDITOR = "Program Editor"
PROGRAM_MANAGER = "Program Manager"
PROGRAM_READER = "Program Reader"
# workflow roles
WORKFLOW_MEMBER = "Workflow Member"
WORKFLOW_MANAGER = "Workflow Manager"
# other roles
OTHER = "other"
CREATORS = CREATOR + "s"
AUDIT_LEAD = "Audit Lead"
AUDITORS = "Auditors"
PRINCIPAL_ASSIGNEES = "Principal " + ASSIGNEES
SECONDARY_ASSIGNEES = "Secondary " + ASSIGNEES
PRIMARY_CONTACTS = "Primary Contacts"
SECONDARY_CONTACTS = "Secondary Contacts"
CONTROL_OPERATORS = "Control Operators"
CONTROL_OWNERS = "Control Owners"
PRODUCT_MANAGERS = "Product Managers"
TECHNICAL_LEADS = "Technical Leads"
TECHNICAL_PMS = "Technical / Program Managers"
LEGAL_COUNSELS = "Legal Counsels"
SYSTEM_OWNERS = "System Owners"

# Some Smoke ACL tests check functionality under this set of roles
IMPORTANT_ASMT_ROLES = [
    ("audit", "auditors"),
    ("assessment", "assignees"),
    ("assessment", "verifiers")
]

# role scopes
SYSTEM = "System"
PRIVATE_PROGRAM = "Private Program"
WORKFLOW = "Workflow"
SUPERUSER = "Superuser"
NO_ACCESS = "No Access"


@memoize
def global_roles():
  """Get global roles as array of dicts"""
  global_roles_url = "/".join([url.API, url.GLOBAL_ROLES])
  return RestClient().send_get(global_roles_url)[
      "{}_collection".format(url.GLOBAL_ROLES)][url.GLOBAL_ROLES]


class ACLRolesIDsMetaClass(type):
  """A class to set ACL role ids"""
  # pylint: disable=invalid-name
  # pylint: disable=no-self-use
  # pylint: disable=not-an-iterable
  # pylint: disable=no-value-for-parameter

  def roles(cls):
    """Return ACL roles."""
    acr_url = "/".join([url.API, url.ACCESS_CONTROL_ROLES])
    return RestClient("").get_object(acr_url).json()[
        "{}_collection".format(url.ACCESS_CONTROL_ROLES)][
        url.ACCESS_CONTROL_ROLES]

  @lazy_property
  def standard_roles(cls):
    """Return standard ACL roles."""
    return cls.roles()

  def _role_id_from_list(cls, roles, object_type, name):
    """Get id of the role by `object_type` and `name` from roles."""
    for role in roles:
      if role["object_type"] == object_type and role["name"] == name:
        role_id = role["id"]
        break
    return role_id

  def object_roles(cls, object_type):
    """Get role ids by `object_type`."""
    roles = []
    for role in cls.roles():
      if role["object_type"] == object_type:
        roles.append(role)
    return roles

  def id_of_role(cls, object_type, name):
    """Get id of the role by `object_type` and `name`."""
    role_id = cls._role_id_from_list(cls.standard_roles, object_type, name)
    if not role_id:
      role_id = cls._role_id_from_list(cls.roles(), object_type, name)
    if not role_id:
      raise ValueError("Invalid role. name {0}, object_type {1}".format(
          name, object_type))
    return role_id

  @property
  def CONTROL_ADMINS(cls):
    return cls.id_of_role(object_type="Control", name="Admin")

  @property
  def ISSUE_ADMINS(cls):
    return cls.id_of_role(object_type="Issue", name="Admin")

  @property
  def OBJECTIVE_ADMINS(cls):
    return cls.id_of_role(object_type="Objective", name="Admin")

  @property
  def RISK_ADMINS(cls):
    return cls.id_of_role(object_type="Risk", name="Admin")

  @property
  def ORG_GROUPS_ADMINS(cls):
    return cls.id_of_role(object_type="OrgGroup", name="Admin")

  @property
  def ASSESSMENT_CREATORS(cls):
    return cls.id_of_role(object_type="Assessment", name="Creators")

  @property
  def ASSESSMENT_ASSIGNEES(cls):
    return cls.id_of_role(object_type="Assessment", name="Assignees")

  @property
  def ASSESSMENT_VERIFIERS(cls):
    return cls.id_of_role(object_type="Assessment", name="Verifiers")

  @property
  def AUDIT_CAPTAINS(cls):
    return cls.id_of_role(object_type="Audit", name="Audit Captains")

  @property
  def AUDITORS(cls):
    return cls.id_of_role(object_type="Audit", name="Auditors")

  @property
  def PROGRAM_MANAGERS(cls):
    return cls.id_of_role(object_type="Program", name="Program Managers")

  @property
  def REVIEWERS(cls):
    return cls.id_of_role(object_type="Review", name="Reviewer")


class ACLRolesIDs(object):
  """Access Control List Roles IDs."""
  # pylint: disable=too-few-public-methods

  __metaclass__ = ACLRolesIDsMetaClass
