# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Workflow related REST services."""

from ggrc.services.registry import service
from ggrc_workflows.services import resource


def contributed_services():
  from ggrc_workflows import models
  return [
      service(models.Workflow.__tablename__, models.Workflow),
      service(models.TaskGroup.__tablename__, models.TaskGroup),
      service(models.TaskGroupTask.__tablename__, models.TaskGroupTask),
      service(models.TaskGroupObject.__tablename__, models.TaskGroupObject),
      service(models.Cycle.__tablename__, models.Cycle),
      service(models.CycleTaskGroup.__tablename__, models.CycleTaskGroup),
      service(models.CycleTaskGroupObjectTask.__tablename__,
              models.CycleTaskGroupObjectTask, resource.CycleTaskResource),
  ]
