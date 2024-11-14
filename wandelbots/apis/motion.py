import asyncio
import json
from typing import AsyncGenerator, Callable, Literal

import wandelbots_api_client as wb_api
from wandelbots_api_client.rest import ApiException
from websockets.exceptions import ConnectionClosedError
from websockets.sync.client import connect

from wandelbots.core.instance import Instance
from wandelbots.exceptions import MotionExecutionError, MotionExecutionInterruptedError
from wandelbots.request.asyncs import post as async_post
from wandelbots.request.syncs import delete, get, post, put
from wandelbots.types import (
    MotionIdsListResponse,
    MoveResponse,
    PlanRequest,
    PlanResponse,
    StreamMoveResponse,
)
from wandelbots.util.logger import _get_logger

logger = _get_logger(__name__)

_get_base_url = lambda url, cell: f"{url}/api/v1/cells/{cell}/motions"


def get_planned_motions(instance: Instance, cell: str) -> list:
    url = f"{_get_base_url(instance.url, cell)}"
    logger.debug(f"Getting planned motions for cell {cell} on: {url}")
    code, response = get(url, instance=instance)
    if code != 200:
        logger.error(f"Failed to get planned motions for cell {cell}")
        return []
    planned_motions = MotionIdsListResponse.from_dict(response).motions
    return planned_motions


def clear_planned_motions(instance: Instance, cell: str) -> None:
    url = f"{_get_base_url(instance.url, cell)}"
    logger.debug(f"Clearing planned motions for cell {cell} on: {url}")
    code, _ = delete(url, instance=instance)
    if code != 200:
        logger.error(f"Failed to clear planned motions for cell {cell}")


def stop_planned_motion(instance: Instance, cell: str, motion: str) -> bool:
    url = f"{_get_base_url(instance.url, cell)}/{motion}/stop"
    logger.debug(f"Stopping planned motion {motion} for cell {cell} on: {url}")
    code, _ = put(url, instance=instance)
    if code != 200:
        logger.error(f"Failed to stop planned motion {motion} for cell {cell}")
        return False
    return True


def plan_motion(instance: Instance, cell: str, plan_request: PlanRequest) -> bool:
    url = f"{_get_base_url(instance.url, cell)}"
    logger.debug(f"Planning motion for cell {cell} on: {url}")
    code, response = post(url, data=plan_request.model_dump(), instance=instance)
    if code != 200:
        logger.error("Failed to plan motion")
        return None
    return PlanResponse.from_dict(response)


async def plan_motion_async(instance: Instance, cell: str, plan_request: PlanRequest) -> bool:
    url = f"{_get_base_url(instance.url, cell)}"
    logger.debug(f"Async planning motion for cell {cell} on: {url}")
    code, response = await async_post(url, data=plan_request.model_dump(), instance=instance)
    if code != 200:
        logger.error("Failed to plan motion")
        return None
    return PlanResponse.from_dict(response)


def _get_wb_api_client(instance: Instance) -> wb_api.ApiClient:
    _url = f"{instance.url}/api/v1"
    _conf = wb_api.Configuration(
        host=_url,
        username=instance.user,
        password=instance.password,
        access_token=instance.access_token,
    )
    return wb_api.ApiClient(_conf)


async def stream_motion_async(
    instance: Instance,
    cell: str,
    motion: str,
    playback_speed: int,
    response_rate: int,
    direction: Literal["forward", "backward"] = "forward",
) -> AsyncGenerator[MoveResponse, None]:
    wb_motion_api = wb_api.MotionApi(_get_wb_api_client(instance))
    logger.debug(f"Connected to Motion API {wb_motion_api.api_client.configuration.host}")
    _func = (
        wb_motion_api.stream_move_forward
        if direction == "forward"
        else wb_motion_api.stream_move_backward
    )
    try:
        async for response in _func(cell, motion, playback_speed, response_rate):
            if hasattr(response, "error") and response.error:
                logger.error(f"Error in motion stream ({response.error.message})")
                raise MotionExecutionError(f"Error in motion stream ({response.error.message})")
            else:
                if hasattr(response, "stop_response") and response.stop_response:
                    stop_code = response.stop_response.stop_code
                    if stop_code == "STOP_CODE_PATH_END":
                        logger.info("Motion has finished")
                        return
                    elif stop_code == "STOP_CODE_USER_REQUEST":
                        logger.info("Motion stopped by user")
                        raise MotionExecutionInterruptedError("Motion stopped by user")
                    elif stop_code == "STOP_CODE_ERROR":
                        stop_message = response.stop_response.message
                        logger.error(f"Error in motion stream ({stop_message})")
                        raise MotionExecutionError(f"Error in motion stream ({stop_message})")
                elif hasattr(response, "move_response") and response.move_response:
                    move_response = response.move_response
                    current_location_on_trajectory = move_response.current_location_on_trajectory
                    time_until_path_end = move_response.time_to_end
                    logger.debug(
                        f"Current location on trajectory: {current_location_on_trajectory} | time to path end: {time_until_path_end}"
                    )
                    yield move_response

    except asyncio.CancelledError:
        logger.info("Motion Stream Cancelled by client.")
        raise
    except ApiException as e:
        logger.error(f"API Exception: {e}")
        raise MotionExecutionError(f"API Exception: {e}")
    finally:
        await wb_motion_api.api_client.close()


def stream_motion(
    instance: Instance,
    cell: str,
    motion: str,
    playback_speed: int,
    response_rate: int,
    direction: Literal["forward", "backward"] = "forward",
    callback: Callable[[MoveResponse], None] = None,
) -> None:
    additional_params = {
        "playback_speed_in_percent": playback_speed,
        "response_rate": response_rate,
    }
    uri = instance.get_socket_uri_with_auth(
        additional_params, f"/cells/{cell}/motions/{motion}/execute{direction}"
    )
    logger.debug(f"Connecting to {uri}")
    with connect(uri) as socket:
        logger.debug(f"Connected to {uri}")
        try:
            while True:
                response = json.loads(socket.recv())
                try:
                    response: StreamMoveResponse = StreamMoveResponse.model_validate(
                        response["result"]
                    )
                except KeyError:
                    logger.warning(f"Received unexpected message: {response}")
                    continue
                if hasattr(response, "error") and response.error:
                    logger.error(f"Error in motion stream ({response.error.message})")
                    raise MotionExecutionError(f"Error in motion stream ({response.error.message})")
                else:
                    if hasattr(response, "stop_response") and response.stop_response:
                        stop_code = response.stop_response.stop_code
                        if stop_code == "STOP_CODE_PATH_END":
                            logger.info("Motion has finished")
                            return
                        elif stop_code == "STOP_CODE_USER_REQUEST":
                            logger.info("Motion stopped by user")
                            raise MotionExecutionInterruptedError("Motion stopped by user")
                        elif stop_code == "STOP_CODE_ERROR":
                            stop_message = response.stop_response.message
                            logger.error(f"Error in motion stream ({stop_message})")
                            raise MotionExecutionError(f"Error in motion stream ({stop_message})")
                    elif hasattr(response, "move_response") and response.move_response:
                        move_response = response.move_response
                        current_location_on_trajectory = (
                            move_response.current_location_on_trajectory
                        )
                        time_until_path_end = move_response.time_to_end
                        logger.debug(
                            f"Current location on trajectory: {current_location_on_trajectory} | time to path end: {time_until_path_end}"
                        )
                        callback(move_response) if callback else None

        except ApiException as e:
            logger.error(f"API Exception: {e}")
            raise MotionExecutionError(f"API Exception: {e}")
        except ConnectionClosedError:
            logger.info("Connection to motion stream closed")
        finally:
            socket.close()
