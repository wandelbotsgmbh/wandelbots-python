# import types from wandelbots api client directly (unmodified)
# to be able to import them from wandelbots.types
# NOTE: Those have to be imported first, in order to be overridden below
from wandelbots_api_client.models import *

# those types extend the wandelbots_api_client.models
# for different purposes, like adding methods or properties
from .vector3d import Vector3d
from .pose import Pose
from .ios import IOValue, IOType
