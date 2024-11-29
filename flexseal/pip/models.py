from typing import Any, Callable, Annotated
from dataclasses import dataclass, field
from pydantic import BaseModel, GetJsonSchemaHandler, TypeAdapter
from packaging.metadata import RawMetadata, Metadata
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from flexseal.util.version import PackageVersionModel


class _MetadataPydanticAnnotation:
    @classmethod
    def _get_raw_adapter(cls) -> TypeAdapter:
        return TypeAdapter(RawMetadata)

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            _source_type: Any,
            _handler: Callable[[Any], core_schema.CoreSchema]
    ) -> core_schema.CoreSchema:
        def validate_from_raw(value: RawMetadata) -> Metadata:
            return Metadata.from_raw(value)

        from_raw_schema = core_schema.chain_schema([
            cls._get_raw_adapter().core_schema,
            core_schema.no_info_plain_validator_function(validate_from_raw)
        ])

        return core_schema.json_or_python_schema(
            json_schema=from_raw_schema,
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(Metadata),
                from_raw_schema
            ]),
        )

    @classmethod
    def __get_pydantic_json_schema__(
            cls,
            _core_schema: core_schema.CoreSchema,
            handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(cls._get_raw_adapter().core_schema)


MetadataModel = Annotated[Metadata, _MetadataPydanticAnnotation]


@dataclass(frozen=True)
class InstallReportArchiveInfoModel(BaseModel):
    hash: str
    hashes: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class InstallReportDownloadInfoModel(BaseModel):
    url: str
    archive_info: InstallReportArchiveInfoModel


@dataclass(frozen=True)
class InstallReportItemModel(BaseModel):
    download_info: InstallReportDownloadInfoModel
    is_direct: bool
    metadata: MetadataModel
    requested: bool
    is_yanked: bool = False
    requested_extras: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class InstallReportModel(BaseModel):
    version: PackageVersionModel
    pip_version: PackageVersionModel
    environment: dict[str, str]
    install: list[InstallReportItemModel]
