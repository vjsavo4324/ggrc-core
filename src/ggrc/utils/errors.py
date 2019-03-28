# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""List of all error and warning messages for the app."""

BAD_REQUEST_MESSAGE = (u"Server error occurred. Please contact your "
                       u"system administrator to receive more details.")

WRONG_STATUS = u"Wrong status."

STOPPED_WARNING = u"Export already canceled. Please wait."

BAD_PARAMS = u"Bad request parameters."

INCORRECT_REQUEST_DATA = u"{job_type} failed due incorrect request data."

INTERNAL_SERVER_ERROR = u"{job_type} failed due to internal server error."

JOB_FAILED = u"{job_type} failed."

PREVIOUS_RUN_FAILED = u"Previous run has failed."

STATUS_SET_FAILED = u"Failed to set job status"

RELOAD_PAGE = u"Try to reload /export page."

MISSING_FILE = u"The file is missing."

WRONG_FILE_TYPE = u"Invalid file type."

MANDATORY_HEADER = u"{} should be set, contains {!r} instead."

WRONG_PERSON_HEADER_FORMAT = u"{} should have JSON object like" \
                             u" {{'email': str}}, contains {!r} instead."

MISSING_REVISION = u"The object you are trying to update/map is broken. " \
                   u"Please contact administrator for help."


DUPLICATE_RESERVED_NAME = u"Attribute name '{attr_name}' already exists " \
                          u"at this object type. Please choose another " \
                          u"attribute name and restart the import."

DUPLICATE_GCAD_NAME = u"Global custom attribute '{attr_name}' already " \
                      u"exists for this object type."

DUPLICATE_CUSTOM_ROLE = u"Custom Role with a name of '{role_name}' already " \
                        u"exists for this object type"

MAPPED_ASSESSMENT = (u"The following Audit cannot be deleted due to existing "
                     u"assessment(s) or  assessment template(s) mappings."
                     u"Please delete assessment(s) or assessment template(s)"
                     u"mapped to this Audit to continue")
