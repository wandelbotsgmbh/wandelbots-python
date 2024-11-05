import numpy as np
import pytest
from scipy.spatial.transform import Rotation as R

from wandelbots.types import Pose, Vector3d


@pytest.fixture
def pose1():
    position = Vector3d.from_list([1.0, 2.0, 3.0])
    orientation = Vector3d.from_list([0.1, 0.2, 0.3])
    return Pose(position=position, orientation=orientation)


@pytest.fixture
def pose2():
    position = Vector3d.from_list([4.0, 5.0, 6.0])
    orientation = Vector3d.from_list([0.4, 0.5, 0.6])
    return Pose(position=position, orientation=orientation)


@pytest.fixture
def identity_matrix():
    return np.eye(4)


@pytest.fixture
def combined_matrix():
    return np.array([[-1, 0, 0, 1], [0, -1, 0, 2], [0, 0, 1, 3], [0, 0, 0, 1]])


def test_pose_from_list():
    """Test creating a Pose from a list."""
    pose_list = [1.0, 2.0, 3.0, 0.1, 0.2, 0.3]
    pose = Pose.from_list(pose_list)
    assert isinstance(pose, Pose), "Pose should be a Pose object"
    assert isinstance(pose.position, Vector3d), "Position should be a Vector3d object"
    assert isinstance(pose.orientation, Vector3d), "Orientation should be a Vector3d object"
    assert pose.as_rotation_matrix().shape == (3, 3), "Rotation matrix should be 3x3"


def test_pose_from_dict():
    """Test creating a Pose from a dictionary."""
    pose_dict = {
        "position": {"x": 1.0, "y": 2.0, "z": 3.0},
        "orientation": {"x": 0.1, "y": 0.2, "z": 0.3},
    }
    pose = Pose(**pose_dict)
    assert isinstance(pose, Pose), "Pose should be a Pose object"
    assert isinstance(pose.position, Vector3d), "Position should be a Vector3d object"
    assert isinstance(pose.orientation, Vector3d), "Orientation should be a Vector3d object"
    assert pose.as_rotation_matrix().shape == (3, 3), "Rotation matrix should be 3x3"


def test_as_rotation_matrix(pose1):
    """Test converting orientation to rotation matrix."""
    rotation_matrix = pose1.as_rotation_matrix()
    assert rotation_matrix.shape == (3, 3), "Rotation matrix should be 3x3"
    assert isinstance(rotation_matrix, np.ndarray), "Rotation matrix should be a NumPy array"


def test_to_homogenous_transformation_matrix(pose1):
    """Test conversion to a 4x4 homogeneous transformation matrix."""
    transformation_matrix = pose1.matrix
    assert transformation_matrix.shape == (4, 4), "Transformation matrix should be 4x4"
    assert np.allclose(transformation_matrix[3, :], [0, 0, 0, 1]), "Last row should be [0, 0, 0, 1]"


def test_pose_multiplication(pose1, pose2):
    """Test pose multiplication."""
    result_pose = pose1 * pose2
    assert isinstance(result_pose, Pose), "Result of pose multiplication should be a Pose object"

    # Test position
    result_position = result_pose.position
    assert isinstance(result_position, Vector3d), "Resulting position should be a Vector3d object"
    assert (
        len([result_position.x, result_position.y, result_position.z]) == 3
    ), "Position should have 3 coordinates"

    # Test orientation
    result_orientation = result_pose.orientation
    assert isinstance(
        result_orientation, Vector3d
    ), "Resulting orientation should be a Vector3d object"
    assert (
        len([result_orientation.x, result_orientation.y, result_orientation.z]) == 3
    ), "Orientation should have 3 components"


def test_matrix_multiplication(pose1, identity_matrix):
    """Test multiplication with a 4x4 matrix."""
    result_pose = pose1 * identity_matrix
    assert isinstance(
        result_pose, Pose
    ), "Multiplying a Pose with a matrix should return a Pose object"
    assert np.allclose(
        result_pose.matrix, pose1.matrix
    ), "Multiplying with identity matrix should return the same pose"


def test_reverse_matrix_multiplication(pose1, identity_matrix):
    """Test right multiplication with a 4x4 matrix."""
    result_pose = identity_matrix * pose1
    assert isinstance(result_pose, Pose), "Right multiplication should return a Pose object"
    assert np.allclose(
        result_pose.matrix, pose1.matrix
    ), "Multiplying by identity matrix should not change the pose"


def test_matrix_multiplication_against_np_dot(pose1, pose2, combined_matrix):
    """Test matrix multiplication against np.dot."""
    result_pose = pose1 * pose2
    result_matrix = pose1.matrix @ pose2.matrix
    assert np.allclose(
        result_pose.matrix, result_matrix
    ), "Matrix multiplication should be consistent with np.dot"

    result_pose = pose1 * combined_matrix
    result_matrix = pose1.matrix @ combined_matrix
    assert np.allclose(
        result_pose.matrix, result_matrix
    ), "Matrix multiplication should be consistent with np.dot"

    result_pose = combined_matrix * pose1
    result_matrix = combined_matrix @ pose1.matrix
    assert np.allclose(
        result_pose.matrix, result_matrix
    ), "Matrix multiplication should be consistent with np.dot"


def test_matrix_to_pose_conversion(pose1):
    """Test matrix-to-pose conversion."""
    matrix = pose1.matrix
    new_pose = pose1._matrix_to_pose(matrix)
    assert isinstance(new_pose, Pose), "Matrix should convert back to a Pose"
    assert np.allclose(matrix, new_pose.matrix), "Matrix conversion should be consistent"


def test_translation_matrix_multiplication(pose1):
    """Test translation matrix multiplication."""
    translation_matrix = np.array(
        [
            [1, 0, 0, 5],  # Translate by 5 along x-axis
            [0, 1, 0, 3],  # Translate by 3 along y-axis
            [0, 0, 1, -2],  # Translate by -2 along z-axis
            [0, 0, 0, 1],
        ]
    )

    result_pose = translation_matrix * pose1

    # Expected position is translated by [5, 3, -2]
    expected_position = pose1.position.as_array() + np.array([5, 3, -2])
    assert np.allclose(
        result_pose.position.as_array(), expected_position
    ), "Position should be translated by [5, 3, -2]"
    # Orientation should stay the same
    assert np.allclose(
        result_pose.orientation.as_array(), pose1.orientation.as_array()
    ), "Orientation should remain unchanged"


def test_rotation_matrix_multiplication():
    """Test rotation matrix multiplication."""
    pose = Pose.from_list([0, 0, 0, 0, 0, 0])
    target_rotation = R.from_euler("xyz", [180, -45, 90], degrees=True)
    transformation_matrix = np.eye(4)
    transformation_matrix[:3, :3] = target_rotation.as_matrix()

    result_pose = transformation_matrix * pose

    # Expected orientation is rotated by 90 degrees around z-axis
    expected_orientation = target_rotation.as_rotvec()
    assert np.allclose(
        result_pose.orientation.as_array(), expected_orientation
    ), "Orientation should be rotated by 90 degrees around z-axis"
    # Position should stay the same
    assert np.allclose(
        result_pose.position.as_array(), pose.position.as_array()
    ), "Position should remain unchanged"
