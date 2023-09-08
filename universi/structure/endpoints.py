from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any

from fastapi import Response
from fastapi.params import Depends
from fastapi.routing import APIRoute
from starlette.routing import BaseRoute

from .._utils import Sentinel


@dataclass(slots=True)
class EndpointAttributesPayload:
    # Fastapi API routes also have "endpoint" and "dependency_overrides_provider" fields.
    # We do not use them because:
    #   1. "endpoint" must not change -- otherwise this versioning is doomed
    #   2. "dependency_overrides_provider" is taken from router's attributes
    #   3. "response_model" must not change for the same reason as endpoint
    # The following for the same reason as enpoint:
    # * response_model_include: SetIntStr | DictIntStrAny
    # * response_model_exclude: SetIntStr | DictIntStrAny
    # * response_model_by_alias: bool
    # * response_model_exclude_unset: bool
    # * response_model_exclude_defaults: bool
    # * response_model_exclude_none: bool
    path: str
    status_code: int
    tags: list[str | Enum]
    # Adding/removing dependencies between versions seems like a bad choice.
    # It makes the system overly complex. Instead, we allow people to
    # overwrite all dependencies of a route at once. Hence you always know exactly
    # which dependencies have been specified, no matter how many migrations you have.

    dependencies: Sequence[Depends]
    summary: str
    description: str
    response_description: str
    responses: dict[int | str, dict[str, Any]]
    deprecated: bool
    methods: list[str]
    operation_id: str
    include_in_schema: bool
    response_class: type[Response]
    name: str
    callbacks: list[BaseRoute]
    openapi_extra: dict[str, Any]
    generate_unique_id_function: Callable[[APIRoute], str]


@dataclass(slots=True)
class EndpointHadInstruction:
    endpoint_path: str
    endpoint_methods: list[str]
    attributes: EndpointAttributesPayload


@dataclass(slots=True)
class EndpointExistedInstruction:
    endpoint_path: str
    endpoint_methods: list[str]


@dataclass(slots=True)
class EndpointDidntExistInstruction:
    endpoint_path: str
    endpoint_methods: list[str]


@dataclass(slots=True)
class EndpointInstructionFactory:
    endpoint_path: str
    endpoint_methods: list[str]

    @property
    def didnt_exist(self) -> EndpointDidntExistInstruction:
        return EndpointDidntExistInstruction(self.endpoint_path, self.endpoint_methods)

    @property
    def existed(self) -> EndpointExistedInstruction:
        return EndpointExistedInstruction(self.endpoint_path, self.endpoint_methods)

    def had(
        self,
        path: str = Sentinel,
        status_code: int = Sentinel,
        tags: list[str | Enum] = Sentinel,
        dependencies: Sequence[Depends] = Sentinel,
        summary: str = Sentinel,
        description: str = Sentinel,
        response_description: str = Sentinel,
        responses: dict[int | str, dict[str, Any]] = Sentinel,
        deprecated: bool = Sentinel,
        methods: list[str] = Sentinel,
        operation_id: str = Sentinel,
        include_in_schema: bool = Sentinel,
        response_class: type[Response] = Sentinel,
        name: str = Sentinel,
        callbacks: list[BaseRoute] = Sentinel,
        openapi_extra: dict[str, Any] = Sentinel,
        generate_unique_id_function: Callable[[APIRoute], str] = Sentinel,
    ):
        return EndpointHadInstruction(
            endpoint_path=self.endpoint_path,
            endpoint_methods=self.endpoint_methods,
            attributes=EndpointAttributesPayload(
                path=path,
                status_code=status_code,
                tags=tags,
                dependencies=dependencies,
                summary=summary,
                description=description,
                response_description=response_description,
                responses=responses,
                deprecated=deprecated,
                methods=methods,
                operation_id=operation_id,
                include_in_schema=include_in_schema,
                response_class=response_class,
                name=name,
                callbacks=callbacks,
                openapi_extra=openapi_extra,
                generate_unique_id_function=generate_unique_id_function,
            ),
        )


def endpoint(endpoint_path: str, endpoint_methods: list[str], /) -> EndpointInstructionFactory:
    return EndpointInstructionFactory(endpoint_path, endpoint_methods)


AlterEndpointSubInstruction = EndpointDidntExistInstruction | EndpointExistedInstruction | EndpointHadInstruction
