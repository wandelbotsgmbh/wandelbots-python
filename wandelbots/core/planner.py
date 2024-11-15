import warnings
from typing import Union

from wandelbots.apis import motion as motion_api
from wandelbots.core.motiongroup import MotionGroup
from wandelbots.core.plan_result import PlanResult
from wandelbots.exceptions import PlanningFailedException, PlanningPartialSuccessWarning
from wandelbots.types import (
    Command,
    CommandSettings,
    IOType,
    IOValue,
    Joints,
    PlanFailedOnTrajectoryResponse,
    PlanRequest,
    PlanResponse,
    PlanSuccessfulResponse,
    Pose,
    SetIO,
)
from wandelbots.util.logger import _get_logger

CommandType = Union[Command, IOValue]


class Planner:
    def __init__(self, motion_group: MotionGroup):
        self.logger = _get_logger(__name__)
        self.instance = motion_group.instance
        self.cell = motion_group.cell
        self.motion_group = motion_group.motion_group
        self.default_tcp = motion_group.default_tcp

    def _from_default_tcp(self, tcp: str) -> str:
        return tcp or self.default_tcp

    def _create_plan_request(
        self, tcp: str, commands: list[Command], start_joints: list[float]
    ) -> PlanRequest:
        return PlanRequest(
            motion_group=self.motion_group,
            start_joint_position=Joints(joints=start_joints),
            commands=commands,
            tcp=tcp,
        )

    def _handle_plan_response(self, response: PlanResponse) -> PlanSuccessfulResponse:
        if response.plan_successful_response:
            success = response.plan_successful_response
            self.logger.info(f"Plan successful, Motion ID: {success.motion}")
            return success

        error_response = (
            response.plan_failed_on_trajectory_response or response.plan_failed_response
        )
        if error_response:
            self.logger.warning(f"Plan failed: {error_response.description}")

            if isinstance(error_response, PlanFailedOnTrajectoryResponse):
                raise PlanningPartialSuccessWarning(
                    message=error_response.description, motion=error_response.motion
                )
            raise PlanningFailedException(f"Plan failed: {error_response.description}")
        self.logger.error("Plan failed with an unknown error")
        raise PlanningFailedException("Plan failed with unknown error")

    def _plan_with_rae(self, plan_request: PlanRequest) -> PlanSuccessfulResponse:
        response = motion_api.plan_motion(
            instance=self.instance, cell=self.cell, plan_request=plan_request
        )
        return self._handle_plan_response(response)

    async def _plan_with_rae_async(self, plan_request: PlanRequest) -> PlanSuccessfulResponse:
        response = await motion_api.plan_motion_async(
            instance=self.instance, cell=self.cell, plan_request=plan_request
        )
        return self._handle_plan_response(response)

    def line(self, pose: Pose, settings: CommandSettings = None) -> Command:
        return Command(line=pose, settings=settings)

    def joint_ptp(self, joints: Joints, settings: CommandSettings = None) -> Command:
        """
        Create a point-to-point (ptp) command in joint space.

        PTP means point-to-point and can vary in implementation by different robot OEMs.
        In NOVA, ptp always performs a linear motion in joint space, regardless of the robot
        being controlled or the speed of movement. This may differ from what OEM code produces
        for the "same" ptp command.
        """
        return Command(joint_ptp=Joints(joints=joints), settings=settings)

    def cartesian_ptp(self, pose: Pose, settings: CommandSettings = None) -> Command:
        """
        Create a point-to-point (ptp) command in Cartesian space.

        PTP means point-to-point and can vary in implementation by different robot OEMs.
        In NOVA, ptp always performs a linear motion in joint space, regardless of the robot
        being controlled or the speed of movement. This may differ from what OEM code produces
        for the "same" ptp command.
        """
        return Command(cartesian_ptp=pose, settings=settings)

    def jptp(self, joints: Joints, settings: CommandSettings = None) -> Command:
        """
        Deprecated: Use joint_ptp instead.

        Create a point-to-point (ptp) command in joint space.

        PTP means point-to-point and can vary in implementation by different robot OEMs.
        In NOVA, ptp always performs a linear motion in joint space, regardless of the robot
        being controlled or the speed of movement. This may differ from what OEM code produces
        for the "same" ptp command.
        """
        warnings.warn("jptp is deprecated, use joint_ptp instead", DeprecationWarning, stacklevel=2)
        return self.joint_ptp(joints, settings)

    def cptp(self, pose: Pose, settings: CommandSettings = None) -> Command:
        """
        Deprecated: Use cartesian_ptp instead.

        Create a point-to-point (ptp) command in Cartesian space.

        PTP means point-to-point and can vary in implementation by different robot OEMs.
        In NOVA, ptp always performs a linear motion in joint space, regardless of the robot
        being controlled or the speed of movement. This may differ from what OEM code produces
        for the "same" ptp command.
        """
        warnings.warn(
            "cptp is deprecated, use cartesian_ptp instead", DeprecationWarning, stacklevel=2
        )
        return self.cartesian_ptp(pose, settings)

    def set_io(self, key: str, value: IOType) -> IOValue:
        return IOValue.from_key_value(key=key, value=value)

    def plan(
        self, trajectory: list[Union[Command, IOValue]], start_joints: list[float], tcp: str = None
    ) -> PlanResult:
        tcp = self._from_default_tcp(tcp)
        move_commands, io_actions = self._resolve_commands(trajectory)
        rae_plan_request = self._create_plan_request(tcp, move_commands, start_joints)
        plan_response = self._plan_with_rae(rae_plan_request)
        return PlanResult(plan_response, io_actions)

    async def plan_async(
        self, trajectory: list[CommandType], start_joints: list[float], tcp: str = None
    ) -> PlanResult:
        tcp = self._from_default_tcp(tcp)
        move_commands, io_actions = self._resolve_commands(trajectory)
        rae_plan_request = self._create_plan_request(tcp, move_commands, start_joints)
        plan_response = await self._plan_with_rae_async(rae_plan_request)
        return PlanResult(plan_response, io_actions)

    @staticmethod
    def _resolve_commands(trajectory: list[CommandType]) -> tuple[list[Command], tuple[SetIO, ...]]:
        """Split-up input trajectory into move commands and io actions."""

        path_param = 0
        move_trajectory: list[Command] = []
        io_actions: list[SetIO] = []

        for command in trajectory:
            if isinstance(command, IOValue):
                io_actions.append(SetIO(io=command, location=path_param))
            else:
                move_trajectory.append(command)
                path_param += 1

        return move_trajectory, tuple(io_actions)
