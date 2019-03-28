# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""List of all error and warning messages for imports."""

ERROR_TEMPLATE = u"Line {line}: {message}"

WRONG_FILE_TYPE = (u"Line {line}: Wrong file type. Only .csv files are"
                   u" supported. Please upload a .csv file.")

MISSING_COLUMN = (u"Line {line}: Missing mandatory column{s} {column_names},"
                  u" when adding object.")

MISSING_CUSTOM_ATTRIBUTE_COLUMN = (u"Line {line}: Missing custom column"
                                   " {column_name}, when adding object.")

WRONG_OBJECT_TYPE = (u"Line {line}: Object type '{object_name}' doesn't "
                     u"exist or can't be imported.")

UNKNOWN_COLUMN = (u"Line {line}: Attribute '{column_name}' does not"
                  u" exist. Column will be ignored.")

DELETE_UNKNOWN_OBJECT = (u"Line {line}: Object '{slug}' does not exist, so it"
                         u" can't be deleted.")

DUPLICATE_COLUMN = (u"Line {line}: Duplicate columns found {duplicates}."
                    u" Object block will be ignored.")

DUPLICATE_VALUE = (u"Line {line}: {column_name} '{value}' already exists."
                   u"Record will be ignored.")

DUPLICATE_IN_MULTI_VALUE = (
    u"Line {line}: {column_name} contains duplicate values. Only a single "
    u"value from each group of identical values will be used. "
    u"Duplicates: {duplicates}"
)

DUPLICATE_VALUE_IN_CSV = (u"Line {line} has the same {column_name} '{value}' "
                          u"as {processed_line}. The line will be ignored.")

MAP_UNMAP_CONFLICT = (u"Line {line}: Object '{slug}' scheduled for mapping and"
                      u" unmapping at the same time. Mapping rule update will"
                      u" be ignored.")

UNKNOWN_OBJECT = (u"Line {line}: {object_type} '{slug}' doesn't exist, so it"
                  u" can't be mapped/unmapped.")

UNKNOWN_USER_WARNING = (u"Line {line}: Specified user '{email}' does not "
                        u"exist. That user will be ignored.")

OWNER_MISSING = (u"Line {line}: {column_name} field does not contain a valid "
                 u"value. You will be assigned as object {column_name}.")

WRONG_MULTI_VALUE = (u"Line {line}: {column_name} contains invalid line. The"
                     u" value '{value}' will be ignored.")

WRONG_VALUE = (u"Line {line}: Field '{column_name}' contains invalid data. The"
               u" value will be ignored.")

WRONG_VALUE_DEFAULT = (u"Line {line}: Field '{column_name}' contains invalid"
                       u" data. The default value will be used.")

WRONG_VALUE_CURRENT = (u"Line {line}: Field '{column_name}' contains invalid"
                       u" data. The current value will be used.")

WRONG_VALUE_ERROR = (u"Line {line}: Field '{column_name}' contains invalid "
                     u"data. The line will be ignored.")

WRONG_REQUIRED_VALUE = (u"Line {line}: Required field {column_name} contains"
                        u" invalid data '{value}'. The default value will be"
                        u" used.")

WRONG_TICKET_STATUS = (u"Line {line}: You are not allowed to autogenerate "
                       u"tickets at Ticket Tracker for Issues at statuses "
                       u"'Fixed', 'Fixed and Verified' and 'Deprecated'. "
                       u"Column '{column_name}' will be set to 'Off'. Please "
                       u"use a manual linking option instead.")

MISSING_VALUE_WARNING = (u"Line {line}: Field '{column_name}' is required. "
                         u"The default value '{default_value}' will be used.")

MISSING_VALUE_ERROR = (u"Line {line}: Field '{column_name}' is required. The "
                       u"line will be ignored.")

PERMISSION_ERROR = (u"Line {line}: You don't have permission to update/delete"
                    u" this record.")

MAPPING_PERMISSION_ERROR = (u"Line {line}: You don't have permission to update"
                            " mappings for {object_type}: {slug}.")

MAPPING_SCOPING_ERROR = (u"Line {line}: You do not have the necessary "
                         u"permissions to {action} scoping objects to "
                         u"directives in this application. Please contact "
                         u"your administrator if you have any questions. "
                         u"Column '{action}:{object_type}' will be ignored.")

DELETE_NEW_OBJECT_ERROR = (u"Line {line}: Tried to create and delete the same"
                           " object {object_type}: {slug} in one import.")

DELETE_CASCADE_ERROR = (u"Line {line}: Cannot delete object {object_type}:"
                        " {slug} without deleting other objects")

UNKNOWN_ERROR = u"Line {line}: Import failed due to unknown error."

INVALID_START_END_DATES = (u"Line {line}: {start_date} can not be after "
                           u"{end_date}. The line will be ignored.")

START_DATE_ON_WEEKEND_ERROR = (u"Line {line}: Task Start Date can not occur "
                               u"on weekends.")

END_DATE_ON_WEEKEND_ERROR = (u"Line {line}: Task Due Date can not occur "
                             u"on weekends.")

UNKNOWN_DATE_FORMAT = (u"Line {line}: Field {column_name} contains invalid "
                       u"date format, use YYYY-MM-DD or MM/DD/YYYY. The line "
                       u"will be ignored.")

WRONG_DATE_FORMAT = (u"Line {line}: Field {column_name} contains invalid "
                     u"date format. Expected MM/DD, but found MM/DD/YYYY, "
                     u"the YYYY part of the date will be ignored.")

UNSUPPORTED_LIST_ERROR = (u"Line {line}: Field {column_name} does not support "
                          u"{value_type}.")

UNSUPPORTED_OPERATION_ERROR = (u"Line {line}: {operation} is not supported. "
                               u"The line will be ignored.")

INVALID_ATTRIBUTE_WARNING = (u"Line {line}: Object does not contain attribute "
                             u"'{column_name}'. The value will be ignored.")

CREATE_INSTANCE_ERROR = (u"Line {line}: New instance creation is denied. "
                         u"The line will be ignored.")

INVALID_STATUS_DATE_CORRELATION = (u"Line {line}: Need to type double dash "
                                   u"'--' into '{date}' cell, if "
                                   u"cycle task state is {deny_states}. "
                                   u"The line will be ignored.")

ONLY_IMPORTABLE_COLUMNS_WARNING = (u"Line {line}: Only the following "
                                   u"attributes are importable: {columns}. "
                                   u"All other columns will be ignored.")

EXPORT_ONLY_WARNING = (u"Line {line}: Field '{column_name}' "
                       u"can not be imported. The value will be ignored.")

ILLEGAL_APPEND_CONTROL_VALUE = ("Line {line}: "
                                "You can not map {mapped_type} to "
                                "{object_type}, because this {mapped_type} is "
                                "not mapped to the related audit.")

UNMODIFIABLE_COLUMN = (u"Line {line}: Column '{column_name}' can not be "
                       u"modified. The value will be ignored.")

ARCHIVED_IMPORT_ERROR = (u"Line {line}: Importing archived instance is "
                         u"prohibited. The line will be ignored.")

VALIDATION_ERROR = (u"Line {line}: Field '{column_name}' validation failed "
                    u"with the following reason: {message}."
                    u" The line will be ignored.")

SINGLE_AUDIT_RESTRICTION = (u"Line {line}: You can not map {mapped_type} to "
                            u"{object_type}, because this {object_type} is "
                            u"already mapped to an {mapped_type}")

UNMAP_AUDIT_RESTRICTION = (u"Line {line}: You can not unmap {mapped_type} "
                           u"from {object_type} because this {object_type} is "
                           u"mapped to an {mapped_type}-scope object.")

UNABLE_TO_EXTRACT_GDRIVE_ID = (u"Line {line}: Unable to extract gdrive_id "
                               u"from {link}. This evidence can't be "
                               u"reused after import")

INVALID_TASKGROUP_MAPPING_WARNING = (u"Line {line}: You can not map "
                                     u"{object_class} to TaskGroup. The value "
                                     u"will be ignored.")

DISALLOW_EVIDENCE_FILE = (u"Line {line}: 'Evidence File' can't be changed "
                          u"via import. Please go on Assessment page and "
                          u"make changes manually. The column will be skipped")

DISALLOW_DOCUMENT_FILE = (u"Line {line}: 'Document File' can't be changed "
                          u"via import. Please go on {parent} page and "
                          u"make changes manually. The column will be skipped")

TASKGROUP_MAPPED_TO_ANOTHER_WORKFLOW = (u"Line {line}: TaskGroup '{slug}' "
                                        u"already exists in the system "
                                        u"and mapped to another "
                                        u"workflow. Please, use different "
                                        u"code for this TaskGroup")

MULTIPLE_ASSIGNEES = (u"Line {line}: Only one assignee (column "
                      u"'{column_name}') can be imported. Please click "
                      u"'Proceed' to choose the first user in alphabetical "
                      u"order as an assignee.")

NO_VALID_USERS_ERROR = (u"Line {line}: Required field '{column_name}' "
                        u"contains not valid users. Only registered users "
                        u"can be assigned to Task Groups.")

NO_VERIFIER_WARNING = (u"Line {line}: Assessment without verifier cannot "
                       u"be moved to {status} state. "
                       u"The value will be ignored.")

UNEXPECTED_ERROR = u"Unexpected error on import."

EXTERNAL_MODEL_IMPORT_RESTRICTION = (u"Line {line}: Trying to import external "
                                     u"model entry.")

READONLY_ACCESS_WARNING = (u"Line {line}: The system is in a "
                           u"read-only mode and is dedicated for SOX needs. "
                           u"The following columns will be ignored: "
                           u"{columns}.")

NON_ADMIN_ACCESS_ERROR = (u"Line {line}: You don't have permissions to make "
                          u"the {object_type} read-only. Please contact your "
                          u"administrator if you have any questions. "
                          u"Column '{column_name}' will be ignored.")
