# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/10 11:28
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: grpc_server_booster.py

from concurrent import futures
import grpc

from agentuniverse.agent_serve.web.rpc.grpc import agentuniverse_service_pb2, \
    agentuniverse_service_pb2_grpc
from agentuniverse.agent_serve.web.rpc.rpc_server import service_run, service_run_async, service_run_result

GRPC_CONFIG = {}

class AgentUniverseService(agentuniverse_service_pb2_grpc.AgentUniverseService):
    """Implementation class of grpc service."""
    def service_run(self, request, context):
        """
        Synchronous invocation of an agent service. Used in rpc implementation.

        Request Args:
            request(`agentuniverse_service_pb2.AgentServiceRequest`):
                service_id(`str`): The id of the agent service.
                params(`str`): A Json String contains agent params passed to service.
                saved(`bool`): Save the request and result into database.
            context: grpc context, needn't pass anything.

        Return:
            Returns agentuniverse_service_pb2.AgentServiceResponse:
            success: This key holds a boolean value indicating the task was
                successfully or not.
            result: This key points to a nested dictionary that includes the
                result of the task.
        """
        service_result = service_run(
            saved=request.saved,
            params=request.params,
            service_id=request.service_id
        )

        return agentuniverse_service_pb2.AgentServiceResponse(
            result=service_result['result'],
            request_id=service_result['request_id'],
            success=service_result['success'],
            message=service_result['message']
        )

    def service_run_async(self, request, context):
        """
        Async invocation of an agent service, return the request id used to
        get result later. Used in rpc implementation.

        Request Args:
            request(`agentuniverse_service_pb2.AgentServiceRequest`):
                service_id(`str`): The id of the agent service.
                params(`str`): A Json String contains agent params passed to service.
                saved(`bool`): Save the request and result into database.
            context: grpc context, needn't pass anything.

        Return:
            Returns agentuniverse_service_pb2.AgentServiceResponse:
            success: This key holds a boolean value indicating the task was
                successfully or not.
            request_id: Stand for a single request task id, can be used in
                service_run_result api to get the result of async task.
        """
        service_result = service_run_async(
            saved=request.saved,
            params=request.params,
            service_id=request.service_id
        )
        return agentuniverse_service_pb2.AgentServiceResponse(
            result=service_result['result'],
            request_id=service_result['request_id'],
            success=service_result['success'],
            message=service_result['message']
        )

    def service_run_result(self, request, context):
        """
        Get the async service result.

        Request Args:
            request(`agentuniverse_service_pb2.AgentResultRequest`):
                request_id(`str`): Request id returned by async run api.
            context: grpc context, needn't pass anything.

        Return:
            Returns agentuniverse_service_pb2.AgentServiceResponse if
            request_id exists in database.
            success: This key holds a boolean value indicating the task was
                successfully or not.
            result: This key points to a nested dictionary that includes the
                result of the task.
        """
        service_result = service_run_result(
            request_id=request.request_id
        )
        return agentuniverse_service_pb2.AgentServiceResponse(
            result=service_result['result'],
            request_id=service_result['request_id'],
            success=service_result['success'],
            message=service_result['message']
        )


def set_grpc_config(configer):
    GRPC_CONFIG["server_port"] = configer.value.get('GRPC', {}).get('server_port', 50051)
    GRPC_CONFIG["max_workers"] = configer.value.get('GRPC', {}).get('max_workers', 10)


def start_grpc_server():
    """Used to start a grpc server, use configer to read grpc server config if
    applied, or use default config of 10 workers and 50051 port."""
    server_port = GRPC_CONFIG.get('server_port', 50051)
    max_workers = GRPC_CONFIG.get('max_workers', 10)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    agentuniverse_service_pb2_grpc.add_AgentUniverseServiceServicer_to_server(
        AgentUniverseService(), server
    )
    server.add_insecure_port(f'[::]:{str(server_port)}')
    server.start()
    print(f"AgentUniverse grpc server start at port {str(server_port)}.")
    server.wait_for_termination()
