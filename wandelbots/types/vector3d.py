import numpy as np
from wandelbots_api_client.models import Vector3d


class Vector3d(Vector3d):
    x: float = 0
    y: float = 0
    z: float = 0

    @staticmethod
    def from_list(list):
        """Create a Vector3d from a list of 3 elements. Assumes the list is in the order [x, y, z]
        and units are in mm."""
        assert len(list) == 3
        return Vector3d(x=list[0], y=list[1], z=list[2])

    def as_array(self) -> np.ndarray:
        """Return the vector as a NumPy array."""
        return np.array([self.x, self.y, self.z])

    def __getitem__(self, index: int) -> float:
        """Get the coordinate at the specified index."""
        return self.as_array()[index]

    def __len__(self) -> int:
        """Returns the number of coordinates."""
        return 3

    def __iter__(self):
        """Returns an iterator over the coordinates."""
        return iter(self.as_array())
