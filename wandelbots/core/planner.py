from wandelbots.util.logger import _get_logger
from wandelbots.types import (
    Pose,
    Command,
    Joints,
    PlanRequest,
    PlanResponse,
    PlanSuccessfulResponse,
    PlanFailedOnTrajectoryResponse,
    CommandSettings,
)
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

    async def _plan_with_rae_async(
        self, plan_request: PlanRequest
    ) -> PlanSuccessfulResponse:
        response = await motion_api.plan_motion_async(
            instance=self.instance, cell=self.cell, plan_request=plan_request
        )
        return self._handle_plan_response(response)

    def line(self, pose: Pose, settings: CommandSettings = None) -> Command:
        return Command(line=pose, settings=settings)

    def jptp(self, joints: Joints, settings: CommandSettings = None) -> Command:
        return Command(joint_ptp=Joints(joints=joints), settings=settings)

    def cptp(self, pose: Pose, settings: CommandSettings = None) -> Command:
        return Command(cartesian_ptp=pose, settings=settings)

    def plan(
        self,
        trajectory: list[Command],
        start_joints: list[float],
        tcp: str = None,
    ) -> PlanSuccessfulResponse:
        tcp = self._from_default_tcp(tcp)
        rae_plan_request = self._create_plan_request(tcp, trajectory, start_joints)
        return self._plan_with_rae(rae_plan_request)

    async def plan_async(
        self,
        trajectory: list[Command],
        start_joints: list[float],
        tcp: str = None,
    ) -> PlanSuccessfulResponse:
        tcp = self._from_default_tcp(tcp)
        rae_plan_request = self._create_plan_request(tcp, trajectory, start_joints)
        return await self._plan_with_rae_async(rae_plan_request)
