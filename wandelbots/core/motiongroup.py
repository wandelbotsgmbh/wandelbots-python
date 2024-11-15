import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable, Literal

from wandelbots.apis import controller as controller_api
from wandelbots.apis import controller_io as controller_io_api
from wandelbots.apis import device_configuration as device_configuration_api
from wandelbots.apis import motion as motion_api
from wandelbots.apis import motion_group as motion_group_api
from wandelbots.apis import motion_group_infos as motion_group_infos_api
from wandelbots.core.instance import Instance
from wandelbots.core.plan_result import PlanResult
from wandelbots.exceptions import MotionGroupConnectionException
from wandelbots.types import IOValue, MoveResponse, Pose
from wandelbots.util.logger import _get_logger


class MotionGroup:
    def __init__(self, instance: Instance, cell: str, motion_group: str, default_tcp: str):
        self.instance = instance
        self.cell = cell
        self.motion_group = motion_group
        self.controller = self._extract_controller_from_motion_group()
        self.default_tcp = default_tcp
        self.logger = _get_logger(__name__)
        self.motions = []
        self.current_motion_in_execution = None

        # initialize connection
        self._connect()
        self.current_mode = self.get_current_mode()

    def _extract_controller_from_motion_group(self):
        """Extract the controller from the motion group which has the format: {id}@{controller}"""
        return self.motion_group.partition("@")[-1]

    def _cell_is_available(self):
        return device_configuration_api.cell_is_available(self.instance, self.cell)

    def _controller_is_available(self):
        controllers = controller_api.get_controllers(self.instance, self.cell)
        return self.controller in controllers

    def _motion_group_is_available(self):
        motion_groups = motion_group_api.get_active_motion_groups(self.instance, self.cell)
        return self.motion_group in motion_groups

    def _connect(self):
        """Establish connection with the motion-group and ensures availability."""
        self.logger.info(f"Connecting to motion-group {self.motion_group} on host {self.instance}")

        if not self._cell_is_available():
            raise MotionGroupConnectionException(f"Cell {self.cell} is not available")

        if not self._controller_is_available():
            raise MotionGroupConnectionException(f"Controller {self.controller} is not available")

        if not self._motion_group_is_available():
            self.logger.info(
                f"Motion group {self.motion_group} is not available, trying to activate it.."
            )
            motion_group_api.activate_motion_group(self.instance, self.cell, self.motion_group)

            if not self._motion_group_is_available():
                raise MotionGroupConnectionException(
                    f"Motion group {self.motion_group} couldn't be activated"
                )

        if self.default_tcp not in self.tcps():
            raise MotionGroupConnectionException(f"TCP {self.default_tcp} is not available")

        self.logger.info(f"Connected to motion-group {self.motion_group} on host {self.instance}")

    def _from_default_tcp(self, tcp: str) -> str:
        """Return the provided TCP or default to the motion-group's default TCP."""
        return tcp or self.default_tcp

    def activate(self):
        motion_group_api.activate_motion_group(self.instance, self.cell, self.motion_group)

    def deactivate(self):
        motion_group_api.deactivate_motion_group(self.instance, self.cell, self.motion_group)

    def tcps(self) -> list[str]:
        return motion_group_infos_api.get_tcps(self.instance, self.cell, self.motion_group)

    def current_joints(self) -> list[float]:
        return motion_group_infos_api.get_current_joint_config(
            self.instance, self.cell, self.motion_group
        )

    def current_tcp_pose(self, tcp=None) -> Pose:
        tcp = self._from_default_tcp(tcp)
        return motion_group_infos_api.get_current_tcp_pose(
            self.instance, self.cell, self.motion_group, tcp
        )

    def get_current_mode(self) -> str:
        current_mode = controller_api.get_current_mode(self.instance, self.cell, self.controller)
        self.logger.info("Current motion-group mode: " + current_mode)

    def set_default_mode_monitor(self):
        self.logger.info("Setting default mode to MODE_MONITOR")
        controller_api.set_default_mode(self.instance, self.cell, self.controller, "MODE_MONITOR")
        self.current_mode = controller_api.get_current_mode(
            self.instance, self.cell, self.controller
        )
        self.logger.info("Current motion-group mode: " + self.current_mode)

    def set_default_mode_control(self):
        self.logger.info("Setting default mode to MODE_CONTROL")
        controller_api.set_default_mode(self.instance, self.cell, self.controller, "MODE_CONTROL")
        self.current_mode = controller_api.get_current_mode(
            self.instance, self.cell, self.controller
        )
        self.logger.info("Current motion-group mode: " + self.current_mode)

    def stop(self):
        if self.current_motion_in_execution:
            motion_api.stop_planned_motion(
                self.instance, self.cell, self.current_motion_in_execution
            )
            self.current_motion_in_execution = None
        else:
            self.logger.warning("No current motion to stop")

    @asynccontextmanager
    async def _async_execution_context(self, motion: str):
        self.logger.info(f"Starting execution of motion {motion}")
        self.current_motion_in_execution = motion
        try:
            yield
        finally:
            self.logger.info(f"Ending execution of motion {motion}")
            self.current_motion_in_execution = None

    async def execute_motion_stream_async(
        self,
        plan_result: PlanResult,
        speed: int,
        response_rate_ms: int = 200,
        direction: Literal["forward", "backward"] = "forward",
    ) -> AsyncGenerator[MoveResponse, None]:
        """Execute a motion asynchronously, yielding MoveResponse objects.
        Has to be used within an 'async for' loop.
        """
        remaining_io_actions = sorted(
            list(plan_result.io_actions), key=lambda x: x.location, reverse=True
        )
        motion = plan_result.plan_response.motion

        async with self._async_execution_context(motion):
            async for response in motion_api.stream_motion_async(
                self.instance, self.cell, motion, speed, response_rate_ms, direction
            ):
                location = response.current_location_on_trajectory
                while remaining_io_actions and remaining_io_actions[-1].location <= location:
                    io_action = remaining_io_actions.pop()
                    self.set_ios([io_action.io])
                    self.logger.info(
                        f"Setting IO {io_action.io.key} to {io_action.io.value} at {location=}"
                    )
                yield response

            # Set all remaining IOs after the motion has finished
            for io_action in remaining_io_actions:
                self.set_ios([io_action.io])
                self.logger.info(
                    f"Setting IO {io_action.io.key} to {io_action.io.value} at end of motion."
                )

    async def execute_motion_async(
        self,
        plan_result: PlanResult,
        speed: int,
        response_rate_ms: int = 200,
        direction: Literal["forward", "backward"] = "forward",
    ) -> None:
        """Execute a motion asynchronously, consuming MoveResponse without yielding.
        This wraps the execute_motion_stream_async method so it can be used without
        calling it withing a 'async for' and instead just 'await' it.
        """
        async with self._async_execution_context(plan_result.plan_response.motion):
            async for _ in self.execute_motion_stream_async(
                plan_result, speed, response_rate_ms, direction
            ):
                pass  # Consuming the response silently

    def _check_if_event_loop_is_running(self) -> bool:
        """Check if an event loop is already running."""
        try:
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False

    def execute_motion(
        self,
        plan_result: PlanResult,
        speed: int,
        response_rate_ms: int = 200,
        direction: Literal["forward", "backward"] = "forward",
        callback: Callable[[MoveResponse], None] = None,
    ) -> None:
        motion_api.stream_motion(
            self.instance,
            self.cell,
            plan_result.plan_response.motion,
            speed,
            response_rate_ms,
            direction,
            callback,
        )

    def is_executing(self) -> bool:
        return self.current_motion_in_execution is not None

    def set_ios(self, values: list[IOValue]) -> None:
        controller_io_api.set_values(self.instance, self.cell, self.controller, values)

    def get_ios(self, ios: list[str]) -> list[IOValue]:
        return controller_io_api.get_values(self.instance, self.cell, self.controller, ios)

    def set_io(self, value: IOValue) -> None:
        self.set_ios([value])

    def get_io(self, key: str) -> IOValue:
        return self.get_ios([key])[0]
