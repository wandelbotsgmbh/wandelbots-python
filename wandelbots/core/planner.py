from wandelbots.util.logger import _get_logger
from wandelbots.types import (
    Circle,
    Pose,
    Command,
    Joints,
    PlanRequest,
    PlanResponse,
    PlanSuccessfulResponse,
    PlanFailedOnTrajectoryResponse,
    CommandSettings,
    IOValue,
    SetIO,
)
from typing import Union
from wandelbots.apis import motion as motion_api
from wandelbots.exceptions import PlanningFailedException, PlanningPartialSuccessWarning
from wandelbots import MotionGroup


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

    @staticmethod
    def _resolve_commands(
        trajectory: list[Union[Command, IOValue]]
    ) -> tuple[list[Command], list[SetIO]]:
        """Split-up input trajectory into move commands and io actions."""

        path_param = 0
        move_trajectory: list[Command] = []
        ios: list[SetIO] = []

        for command in trajectory:
            if isinstance(command, IOValue):
                ios.append(SetIO(io=command, location=path_param))
            else:
                move_trajectory.append(command)
                path_param += 1

        return move_trajectory, ios

    async def _plan_with_rae_async(
        self, plan_request: PlanRequest
    ) -> PlanSuccessfulResponse:
        response = await motion_api.plan_motion_async(
            instance=self.instance, cell=self.cell, plan_request=plan_request
        )
        return self._handle_plan_response(response)

    def line(self, target: Pose, settings: CommandSettings = None) -> Command:
        return Command(line=target, settings=settings)

    def arc(self, via: Pose, target: Pose, settings: CommandSettings = None) -> Command:
        return Command(
            circle=Circle(via_pose=via, target_pose=target), settings=settings
        )

    def jptp(self, target: Joints, settings: CommandSettings = None) -> Command:
        return Command(joint_ptp=Joints(joints=target), settings=settings)

    def cptp(self, target: Pose, settings: CommandSettings = None) -> Command:
        return Command(cartesian_ptp=target, settings=settings)

    def set_io(self, key: str, value: Union[str, bool, float]):
        return IOValue.from_key_value(key, value)

    def plan(
        self,
        trajectory: list[Union[Command, IOValue]],
        start_joints: list[float],
        tcp: str = None,
    ) -> tuple[PlanSuccessfulResponse, list[SetIO]]:
        tcp = self._from_default_tcp(tcp)
        move_commands, io_actions = self._resolve_commands(trajectory)
        rae_plan_request = self._create_plan_request(tcp, move_commands, start_joints)
        return self._plan_with_rae(rae_plan_request), io_actions

    async def plan_async(
        self, trajectory: list[Command], start_joints: list[float], tcp: str = None
    ) -> tuple[PlanSuccessfulResponse, list[SetIO]]:
        tcp = self._from_default_tcp(tcp)
        move_commands, io_actions = self._resolve_commands(trajectory)
        rae_plan_request = self._create_plan_request(tcp, move_commands, start_joints)
        return await self._plan_with_rae_async(rae_plan_request), io_actions
