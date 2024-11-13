from wandelbots.types import PlanSuccessfulResponse, SetIO


class PlanResult:
    def __init__(self, plan_response: PlanSuccessfulResponse, io_actions: tuple[SetIO, ...] = ()):
        self.plan_response = plan_response
        self.io_actions = io_actions
        self.motion = plan_response.motion
