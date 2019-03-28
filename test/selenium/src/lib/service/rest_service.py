# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Create and manipulate objects via REST API."""
# pylint: disable=too-few-public-methods

import json

import requests

from lib import environment, factory, url, constants
from lib.constants import objects, messages, roles
from lib.entities import entities_factory
from lib.entities.entities_factory import (
    PeopleFactory, CustomAttributeDefinitionsFactory, AssessmentsFactory,
    AccessControlRolesFactory)
from lib.entities.entity import Representation
from lib.service.rest import client, query
from lib.utils import help_utils, test_utils, string_utils


class BaseRestService(object):
  """Base class for business layer's services objects."""
  def __init__(self, endpoint):
    self.endpoint = endpoint
    self.client = client.RestClient(self.endpoint)
    self.entities_factory_cls = factory.get_cls_entity_factory(
        object_name=self.endpoint)

  def create_list_objs(self, entity_factory, count, attrs_to_factory=None,
                       **attrs_for_template):
    # pylint: disable=fixme
    """Create and return list of objects used entities factories,
    REST API service and attributes to make JSON template to request.
    As default entity factory is generating random objects,
    if 'attrs_for_factory' is not None then factory is generating objects
    according to 'attrs_for_factory' (dictionary of attributes).
    """
    list_factory_objs = []
    list_attrs = []
    for _ in xrange(count):
      factory_obj = entity_factory().create(
          is_add_rest_attrs=True,
          **(attrs_to_factory if attrs_to_factory else {}))
      list_factory_objs.append(factory_obj)
      list_attrs.append(self.get_items_from_resp(self.client.create_object(
          **dict(factory_obj.__dict__.items() + attrs_for_template.items()))))
    return [
        self.set_obj_attrs(obj=obj, attrs=attrs, **attrs_for_template)
        for attrs, obj in zip(list_attrs, list_factory_objs)]

  def update_list_objs(self, entity_factory, list_objs_to_update,
                       attrs_to_factory=None, **attrs_for_template):
    """Update and return list of objects used entities factories,
    REST API service and attributes to make JSON template to request.
    As default entity factory is generating random objects,
    if 'attrs_for_factory' is not None then factory is generating objects
    according to 'attrs_for_factory' (dictionary of attributes).
    """
    list_new_objs = [entity_factory().create(
        is_add_rest_attrs=True,
        **(attrs_to_factory if attrs_to_factory else {}))
        for _ in xrange(len(list_objs_to_update))]
    list_new_attrs = [
        self.get_items_from_resp(
            self.client.update_object(
                href=old_obj.href,
                **dict({k: v for k, v in new_obj.__dict__.iteritems() if
                        k != "href"}.items() + attrs_for_template.items()))
        ) for old_obj, new_obj in zip(list_objs_to_update, list_new_objs)]
    return [
        self.set_obj_attrs(obj=new_obj, attrs=new_attrs, **new_obj.__dict__)
        for new_attrs, new_obj in zip(list_new_attrs, list_new_objs)]

  def update_obj(self, obj, **attrs):
    """Update attributes values of existing object via REST API."""
    return self.set_obj_attrs(obj=obj, attrs=self.get_items_from_resp(
        self.client.update_object(href=obj.href, **attrs)), **obj.__dict__)

  @staticmethod  # noqa: ignore=C901
  def get_items_from_resp(resp, timeout=constants.ux.MAX_USER_WAIT_SECONDS):
    """Check response (waiting object of requests library) from server and get
    items {key: value} from it."""
    def get_items_from_resp():
      """Get items from response."""
      def get_extra_items(resp_dict):
        """Get extra items {key: value} that used in entities."""
        extra = {}
        if resp_dict.get("selfLink"):
          extra.update({"href": resp_dict.get("selfLink")})
        if resp_dict.get("viewLink"):
          extra.update(
              {"url": environment.app_url + resp_dict.get("viewLink")[1:]})
        return extra
      if isinstance(resp, requests.models.Response):
        try:
          resp_text = json.loads(resp.text, encoding="utf-8")
        except UnicodeDecodeError as unicode_err:
          raise requests.exceptions.ContentDecodingError(
              messages.ExceptionsMessages.err_server_req_resp.format(
                  resp.request.body,
                  resp.status_code + unicode_err, resp.text))
        resp_status_code = resp.status_code
        req_method = resp.request.method
        is_query_resp = False
        # check response from server
        if resp_status_code == client.RestClient.STATUS_CODES["OK"]:
          # 'POST' request methods
          if req_method == "POST" and isinstance(resp_text, list):
            # REST API: [[201, {resp}]] to {resp}
            if len(resp_text[0]) == 2 and resp_text[0][0] == 201:
              resp_text = resp_text[0][1]
            # QUERY API: [[{resp}]] to {resp}
            elif len(resp_text[0]) == 1 and resp_text[0] != 201:
              is_query_resp = True
              resp_text = resp_text[0]
          # 'PUT' request methods
          if req_method == "PUT":
            pass
        # {resp} == {key: {value}}
        if isinstance(resp_text, dict) and len(resp_text) == 1:
          # {key: {value}} to {value}
          resp_text = resp_text.itervalues().next()
          return (dict(resp_text.items() +
                       ({}.items() if is_query_resp else
                        get_extra_items(resp_text).items())))
        else:
          resp_code, resp_message = resp_text[0]
          raise requests.exceptions.ContentDecodingError(
              messages.ExceptionsMessages.err_server_req_resp.format(
                  resp.request.body, resp_code, resp_message))
      else:
        raise requests.exceptions.RequestException(
            messages.ExceptionsMessages.err_server_resp.format(resp))
    return test_utils.wait_for(get_items_from_resp, timeout)

  @staticmethod
  def set_obj_attrs(obj, attrs, **kwargs):
    """Update object according to new attributes exclude "type" due of objects
    assertion specific, and keyword arguments -
    attributes witch used to make JSON template to request and witch contain
    fully objects descriptions as dictionary.
    """
    obj.__dict__.update({k: v for k, v in attrs.iteritems()
                         if v and k not in ["type", ]})
    if kwargs:
      # for Audit objects
      if kwargs.get("program"):
        obj.program = kwargs["program"]
      # for Assessment, Assessment Template objects
      if kwargs.get("audit"):
        obj.audit = kwargs["audit"]
    return obj

  def create_obj(self, factory_params=None, **attrs_for_template):
    return self.create_objs(1, factory_params=factory_params,
                            **attrs_for_template)[0]

  def create_objs(self, count, factory_params=None, **attrs_for_template):
    """Create new objects via REST API and return list of created objects with
    filtered attributes.
    """
    list_objs = self.create_list_objs(
        entity_factory=self.entities_factory_cls, count=count,
        attrs_to_factory=factory_params, **attrs_for_template)
    return Representation.filter_objs_attrs(
        objs=list_objs,
        attrs_to_include=Representation.all_attrs_names())

  def update_objs(self, objs, factory_params=None, **attrs_for_template):
    """Update existing objects via REST API and return list of updated objects
    with filtered attributes.
    """
    list_objs = self.update_list_objs(
        entity_factory=self.entities_factory_cls,
        list_objs_to_update=help_utils.convert_to_list(objs),
        attrs_to_factory=factory_params, **attrs_for_template)
    return Representation.filter_objs_attrs(
        objs=list_objs,
        attrs_to_include=Representation.all_attrs_names())

  def delete_objs(self, objs):
    """Delete existing objects via REST API."""
    return [self.client.delete_object(href=obj.href) for
            obj in help_utils.convert_to_list(objs)]


class HelpRestService(object):
  """Help class for interaction with business layer's services objects."""
  def __init__(self, endpoint):
    self.endpoint = endpoint
    self.client = client.RestClient(self.endpoint)


class ControlsService(BaseRestService):
  """Service for working with Controls entities."""
  def __init__(self):
    super(ControlsService, self).__init__(url.CONTROLS)


class ObjectivesService(BaseRestService):
  """Service for working with Objectives entities."""
  def __init__(self):
    super(ObjectivesService, self).__init__(url.OBJECTIVES)


class ProgramsService(BaseRestService):
  """Service for working with Programs entities."""
  def __init__(self):
    super(ProgramsService, self).__init__(url.PROGRAMS)


class AuditsService(BaseRestService):
  """Service for working with Audits entities."""
  def __init__(self):
    super(AuditsService, self).__init__(url.AUDITS)


class AssessmentTemplatesService(BaseRestService):
  """Service for working with Assessment Templates entities."""
  def __init__(self):
    super(AssessmentTemplatesService, self).__init__(url.ASSESSMENT_TEMPLATES)


class AssessmentsService(BaseRestService):
  """Service for working with Assessments entities."""
  def __init__(self):
    super(AssessmentsService, self).__init__(url.ASSESSMENTS)


class IssuesService(BaseRestService):
  """Service for working with Issues entities."""
  def __init__(self):
    super(IssuesService, self).__init__(url.ISSUES)


class RisksService(BaseRestService):
  """Service for working with Risks entities."""
  def __init__(self):
    super(RisksService, self).__init__(url.RISKS)


class CustomAttributeDefinitionsService(BaseRestService):
  """Service for working with Custom Attributes entities."""
  def __init__(self):
    super(CustomAttributeDefinitionsService, self).__init__(
        url.CUSTOM_ATTRIBUTES)

  def create_dashboard_gcas(self, obj_type, count=1):
    """Create 'Dashboard' CAs via rest according to passed obj_type and count.
    """
    return [self.create_objs(1, CustomAttributeDefinitionsFactory().
                             create_dashboard_ca(obj_type.lower()).__dict__)[0]
            for _ in xrange(count)]


class PeopleService(BaseRestService):
  """Service for working with People entities."""
  def __init__(self):
    super(PeopleService, self).__init__(url.PEOPLE)


class UserRolesService(BaseRestService):
  """Service for working with User Roles entities."""
  def __init__(self):
    super(UserRolesService, self).__init__(url.USER_ROLES)


class AccessControlRolesService(BaseRestService):
  """Service for working with Access Control Roles entities."""
  def __init__(self):
    super(AccessControlRolesService, self).__init__(url.ACL_ROLES)

  def create_acl_role(self, **attrs):
    """Create ACL role."""
    acl_factory = AccessControlRolesFactory()
    allowed_name_chars = string_utils.Symbols(additional_exclude='*')
    acr_name = acl_factory.generate_string(
        attrs["object_type"],
        allowed_chars=allowed_name_chars.standard_chars
    )
    return self.create_obj(
        acl_factory.create(name=acr_name, **attrs).__dict__)


class RelationshipsService(HelpRestService):
  """Service for creating relationships between entities."""
  def __init__(self):
    super(RelationshipsService, self).__init__(url.RELATIONSHIPS)

  def map_objs(self, src_obj, dest_objs, **attrs_for_template):
    """Create relationship from source to destination objects and
    return created.
    """
    return [self.client.create_object(
        type=objects.get_singular(self.endpoint), source=src_obj.__dict__,
        destination=dest_obj.__dict__, **attrs_for_template) for
        dest_obj in help_utils.convert_to_list(dest_objs)]


class ReviewService(BaseRestService):
  """Service for working with entities reviews."""
  def __init__(self):
    super(ReviewService, self).__init__(url.REVIEWS)

  def request_review(self, obj, person):
    """Add reviewer to object.
    Returns obj with added review."""
    review_attrs = {
        "reviewers": person, "reviewable": obj.repr_min_dict()}
    review = self.create_obj(factory_params=review_attrs)
    # reviewers field contains list of reviewer emails
    obj.review = {
        "status": review.status,
        "reviewers": review.reviewers,
        "last_reviewed_by": ""}
    return obj


class AssessmentsFromTemplateService(HelpRestService):
  """Service for creating assessments from templates."""
  def __init__(self):
    super(AssessmentsFromTemplateService, self).__init__(url.ASSESSMENTS)

  def create_assessments(self, audit, template, snapshots):
    """Create assessments from template."""
    assessments = []
    for snapshot in snapshots:
      assessment = entities_factory.AssessmentsFactory().create()
      assessment.update_attrs(audit=audit, template=template, object=snapshot)
      response = self.client.create_object(**assessment.__dict__)
      attrs = BaseRestService.get_items_from_resp(response)
      assessment = AssessmentsFactory().create()
      assessment.__dict__.update({k: v for k, v in attrs.iteritems()
                                  if v and k not in ["type", ]})
      for acr_name in ("assignees", "verifiers"):
        people = getattr(template, acr_name)
        if people == roles.PRINCIPAL_ASSIGNEES:
          people = snapshot.principal_assignees
        elif people == roles.AUDITORS:
          people = audit.auditors
        elif people == "Audit Captain":
          people = audit.audit_captains
        # handle other roles if needed
        if not people:
          people = audit.audit_captains
        setattr(assessment, acr_name, people)
      assessments.append(assessment)
    return assessments


class ObjectsInfoService(HelpRestService):
  """Service for getting information about entities."""
  def __init__(self):
    super(ObjectsInfoService, self).__init__(url.QUERY)

  def get_snapshoted_obj(self, origin_obj, paren_obj):
    """Get and return snapshoted object according to 'origin_obj' and
    'paren_obj'.
    """

    def get_response():
      """Get response from query."""
      return self.client.create_object(
          type=self.endpoint,
          object_name=objects.get_obj_type(objects.SNAPSHOTS),
          filters=query.Query.expression_get_snapshoted_obj(
              obj_type=origin_obj.type, obj_id=origin_obj.id,
              parent_type=paren_obj.type,
              parent_id=paren_obj.id))

    def get_response_values():
      """Get values fom responese."""
      return json.loads(
          get_response().text, encoding="utf-8")[0]["Snapshot"]["values"]

    test_utils.wait_for(
        get_response_values,
        constants.ux.MAX_USER_WAIT_SECONDS * 2)
    snapshoted_obj_dict = (
        BaseRestService.get_items_from_resp(get_response()).get("values")[0])
    return Representation.repr_dict_to_obj(snapshoted_obj_dict)

  def get_obj(self, obj):
    """Get and return object according to 'obj.type' and 'obj.id'."""
    obj_dict = (BaseRestService.get_items_from_resp(self.client.create_object(
        type=self.endpoint, object_name=unicode(obj.type),
        filters=query.Query.expression_get_obj_by_id(obj.id))).get(
        "values")[0])
    return Representation.repr_dict_to_obj(obj_dict)

  def get_comment_obj(self, paren_obj, comment_description):
    """Get and return comment object according to 'paren_obj' type) and
    comment_description 'paren_obj'. As default 'is_sort_by_created_at' and if
    even comments have the same descriptions query return selection w/ latest
    created datetime.
    """
    comment_obj_dict = (
        BaseRestService.get_items_from_resp(self.client.create_object(
            type=self.endpoint,
            object_name=objects.get_obj_type(objects.COMMENTS),
            filters=query.Query.expression_get_comment_by_desc(
                parent_type=paren_obj.type, parent_id=paren_obj.id,
                comment_desc=comment_description),
            order_by=[{"name": "created_at", "desc": True}])).get("values")[0])
    return Representation.repr_dict_to_obj(comment_obj_dict)

  def get_person(self, email):
    """Get and return person object by email"""
    attrs = (
        BaseRestService.get_items_from_resp(self.client.create_object(
            type=self.endpoint,
            object_name=objects.get_obj_type(objects.PEOPLE),
            filters=query.Query.expression_get_person_by_email(
                email=email))).get("values")[0])
    person = PeopleFactory().create()
    person.__dict__.update({k: v for k, v in attrs.iteritems()
                            if v and k not in ["type", ]})
    return person
