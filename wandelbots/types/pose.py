import os
import sys
import numpy as np

from pydantic import field_validator
from wandelbots_api_client.models import Pose
from wandelbots_api_client.models import Vector3d as Vector3dBase
from wandelbots.types.vector3d import Vector3d


from typing import Union
from scipy.spatial.transform import Rotation as R


class Pose(Pose):
    position: Vector3d
    orientation: Vector3d

    __array_priority__ = 1000  # Give Pose higher priority over NumPy arrays (required for __rmul__)

    @field_validator("position", "orientation", mode="before")
    def validate_vector3d(cls, value):
        """Ensure the Vector3d class used is the custom one"""
        if isinstance(value, dict):
            return Vector3d(**value)
        elif isinstance(value, Vector3dBase):
            return Vector3d(x=value.x, y=value.y, z=value.z)
        return value

    @staticmethod
    def from_list(list):
        """Create a Pose from a list of 6 elements. Assumes the list is in the order [x, y, z, rx, ry, rz]"""
        assert len(list) == 6
        return Pose(
            position=Vector3d(x=list[0], y=list[1], z=list[2]),
            orientation=Vector3d(x=list[3], y=list[4], z=list[5]),
        )

    def copy(self):
        """Returns a copy of the current pose object."""
        return Pose(
            position=Vector3d(x=self.position.x, y=self.position.y, z=self.position.z),
            orientation=Vector3d(x=self.orientation.x, y=self.orientation.y, z=self.orientation.z),
        )

    def as_rotation_matrix(self):
        """Converts orientation vector (axis-angle) into a 3x3 rotation matrix. Ignoring position."""
        return R.from_rotvec(self.orientation.as_array()).as_matrix()

    def _to_homogenous_transformation_matrix(self):
        """Converts the pose (position and rotation vector) to a 4x4 homogeneous transformation matrix."""
        rotation_vec = [self.orientation.x, self.orientation.y, self.orientation.z]
        rotation_matrix = R.from_rotvec(rotation_vec).as_matrix()
        mat = np.eye(4)
        mat[:3, :3] = rotation_matrix
        mat[:3, 3] = [self.position.x, self.position.y, self.position.z]
        return mat

    def _matrix_to_pose(self, matrix: np.ndarray) -> Pose:
        """Converts a homogeneous transformation matrix to a Pose."""
        rotation_matrix = matrix[:3, :3]
        position = matrix[:3, 3]
        rotation_vec = R.from_matrix(rotation_matrix).as_rotvec()
        return Pose(
            position=Vector3d(x=position[0], y=position[1], z=position[2]),
            orientation=Vector3d(x=rotation_vec[0], y=rotation_vec[1], z=rotation_vec[2]),
        )

    @property
    def matrix(self) -> np.ndarray:
        """Returns the homogeneous transformation matrix."""
        return self._to_homogenous_transformation_matrix()

    @property
    def inverse(self) -> Pose:
        """Returns the inverse of the current pose."""
        mat = np.linalg.inv(self.matrix)
        return self._matrix_to_pose(mat)

    def translate(self, vector: Vector3d):
        """Translates the pose by the given vector."""
        self.position.x += vector.x
        self.position.y += vector.y
        self.position.z += vector.z
        return self

    def __mul__(self, other: Union["Pose", np.ndarray]) -> "Pose":
        """Allows [Pose | Matrix] * self for transformation application."""
        if isinstance(other, Pose):
            transformed_matrix = np.dot(self.matrix, other.matrix)
            return self._matrix_to_pose(transformed_matrix)
        elif isinstance(other, np.ndarray):
            assert other.shape == (4, 4)
            transformed_matrix = np.dot(self.matrix, other)
            return self._matrix_to_pose(transformed_matrix)
        else:
            raise ValueError(f"Cannot multiply Pose with {type(other)}")

    def __rmul__(self, other: Union["Pose", np.ndarray]) -> "Pose":
        """Allows self * [Pose | Matrix] for transformation application."""
        if isinstance(other, Pose):
            transformed_matrix = np.dot(other.matrix, self.matrix)
            return self._matrix_to_pose(transformed_matrix)
        elif isinstance(other, np.ndarray):
            assert other.shape == (4, 4)
            transformed_matrix = np.dot(other, self.matrix)
            return self._matrix_to_pose(transformed_matrix)
        else:
            raise ValueError(f"Cannot multiply {type(other)} with Pose")

    def __iter__(self):
        """Returns an iterator over the position and orientation values."""
        return iter(
            [
                self.position.x,
                self.position.y,
                self.position.z,
                self.orientation.x,
                self.orientation.y,
                self.orientation.z,
            ]
        )

    def __str__(self):
        # Check if ANSI colors should be disabled (e.g., when running in CI or non-interactive terminal)
        use_ansi = (
            os.getenv("CI") is None
            and hasattr(sys.stdout, "fileno")
            and callable(sys.stdout.fileno)
            and os.isatty(sys.stdout.fileno())
        )

        # ANSI escape codes for colors and bold formatting
        bold_start = "\033[1m" if use_ansi else ""
        bold_end = "\033[0m" if use_ansi else ""

        red = "\033[31m" if use_ansi else ""
        green = "\033[32m" if use_ansi else ""
        blue = "\033[34m" if use_ansi else ""
        reset = "\033[0m" if use_ansi else ""

        # Extract position and rotation values
        pos_values = list(self.position.to_dict().values())
        rot_values = list(self.orientation.to_dict().values())

        # Format each component with bold, colors, and fixed width for alignment
        pos_str = (
            f"{red}{bold_start}{int(pos_values[0]):>5}{bold_end}{reset}, "
            f"{green}{bold_start}{int(pos_values[1]):>5}{bold_end}{reset}, "
            f"{blue}{bold_start}{int(pos_values[2]):>5}{bold_end}{reset}"
        )

        rot_str = (
            f"{red}{bold_start}{rot_values[0]:>5.2f}{bold_end}{reset}, "
            f"{green}{bold_start}{rot_values[1]:>5.2f}{bold_end}{reset}, "
            f"{blue}{bold_start}{rot_values[2]:>5.2f}{bold_end}{reset}"
        )

        # Return the formatted string with ANSI escape codes for aligned Position and Rotation
        return f"Position: [{pos_str}]\nRotation: [{rot_str}]"
