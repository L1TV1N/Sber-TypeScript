import base64
import json
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from agent import chain, document_mapping_chain, mapping_chain
from api.v1.schemas import (
    GenerateFromExampleResponse,
    GenerateTsRequest,
    GenerateTsResponse,
    LogsResponse,
    ValidateTsRequest,
    ValidateTsResponse,
)
from services.file_preview import build_file_preview
from services.json_schema import extract_json_structure
from services.llm_postprocess import (
    looks_like_typescript,
    normalize_typescript_code,
    preview_is_informative,
)
from services.project_logger import (
    clear_log_file,
    log_exception,
    log_info,
    log_warning,
    read_recent_logs,
)
from services.ts_validator import validate_typescript_on_source
from services.tabular_mapping import enrich_mapping_with_headers
from services.tabular_ts_template import build_tabular_typescript, normalize_mapping_response
from services.document_ts_template import (
    build_document_typescript,
    enrich_document_mapping,
    normalize_document_mapping_response,
)

api_router = APIRouter()


@api_router.get("/health")
def health():
    log_info("health_check_requested")
    return {
        "status": "ok",
        "service": "sber-ts-generator",
    }


@api_router.get("/logs", response_model=LogsResponse)
def get_logs(limit: int = 200):
    limit = max(1, min(limit, 1000))
    lines = read_recent_logs(limit=limit)
    return LogsResponse(status="ok", lines=lines)


@api_router.post("/logs/clear")
def clear_logs():
    clear_log_file()
    log_info("project_log_cleared")
    return {"status": "ok"}


@api_router.post("/prediction", response_model=GenerateTsResponse)
async def prediction(request: GenerateTsRequest):
    try:
        log_info(
            "prediction_request_received",
            file_name=request.file_name,
            file_extension=request.file_name.split(".")[-1].lower(),
            target_json_length=len(request.target_json_example or ""),
            file_base64_length=len(request.file_base64 or ""),
        )

        extracted_preview = build_file_preview(
            file_name=request.file_name,
            base64file=request.file_base64,
        )
        log_info(
            "file_preview_built",
            file_name=request.file_name,
            preview_length=len(extracted_preview),
        )

        target_schema = extract_json_structure(request.target_json_example)
        log_info(
            "target_schema_extracted",
            schema_length=len(target_schema),
        )

        informative, reason = preview_is_informative(extracted_preview)
        if not informative:
            log_warning(
                "preview_not_informative",
                file_name=request.file_name,
                reason=reason,
            )
            return GenerateTsResponse(
                content="",
                extracted_preview=extracted_preview,
                target_schema=target_schema,
                status="warning",
                valid_ts=False,
                message=reason,
            )

        file_extension = request.file_name.split(".")[-1].lower()

        if file_extension in {"csv", "xls", "xlsx"}:
            log_info(
                "gigachat_analysis_started",
                file_name=request.file_name,
                file_extension=file_extension,
            )

            raw_mapping = mapping_chain.invoke(
                {
                    "file_name": request.file_name,
                    "file_extension": file_extension,
                    "target_schema": target_schema,
                    "extracted_preview": extracted_preview,
                }
            )
            log_info("gigachat_analysis_completed", raw_result_length=len(raw_mapping or ""))

            try:
                parsed_mapping = normalize_mapping_response(raw_mapping)
            except Exception:
                parsed_mapping = {}

            enriched_mapping = enrich_mapping_with_headers(
                mapping_spec=parsed_mapping,
                preview_json=extracted_preview,
                target_json_example=request.target_json_example,
            )
            normalized_result = build_tabular_typescript(
                target_json_example=request.target_json_example,
                mapping_spec=enriched_mapping,
            )
            valid_ts = looks_like_typescript(normalized_result)
        elif file_extension in {"pdf", "docx"}:
            log_info(
                "gigachat_document_analysis_started",
                file_name=request.file_name,
                file_extension=file_extension,
            )
            raw_plan = document_mapping_chain.invoke(
                {
                    "file_name": request.file_name,
                    "file_extension": file_extension,
                    "target_schema": target_schema,
                    "extracted_preview": extracted_preview,
                }
            )
            log_info("gigachat_document_analysis_completed", raw_result_length=len(raw_plan or ""))

            try:
                parsed_plan = normalize_document_mapping_response(raw_plan)
            except Exception:
                parsed_plan = {}

            enriched_plan = enrich_document_mapping(
                mapping_spec=parsed_plan,
                target_json_example=request.target_json_example,
            )
            normalized_result = build_document_typescript(
                target_json_example=request.target_json_example,
                mapping_spec=enriched_plan,
                file_extension=file_extension,
            )
            valid_ts = looks_like_typescript(normalized_result)
        else:
            log_info(
                "llm_request_started",
                file_name=request.file_name,
                file_extension=file_extension,
            )

            raw_result = chain.invoke(
                {
                    "file_name": request.file_name,
                    "file_extension": file_extension,
                    "target_schema": target_schema,
                    "extracted_preview": extracted_preview,
                }
            )

            log_info(
                "llm_response_received",
                raw_result_length=len(raw_result or ""),
            )

            normalized_result = normalize_typescript_code(raw_result)
            valid_ts = looks_like_typescript(normalized_result)

        log_info(
            "llm_response_normalized",
            normalized_length=len(normalized_result or ""),
            valid_ts=valid_ts,
        )

        if not valid_ts:
            log_warning(
                "typescript_validation_warning",
                message="LLM returned a response that needs manual review.",
            )

        response = GenerateTsResponse(
            content=normalized_result,
            extracted_preview=extracted_preview,
            target_schema=target_schema,
            status="ok" if valid_ts else "warning",
            valid_ts=valid_ts,
            message="" if valid_ts else "LLM returned a response that needs manual review.",
        )

        log_info(
            "prediction_request_completed",
            status=response.status,
            valid_ts=response.valid_ts,
        )
        return response

    except Exception as ex:
        log_exception("prediction_request_failed", ex)
        return JSONResponse(
            status_code=500,
            content={"message": str(ex)},
        )


@api_router.post("/validate-ts", response_model=ValidateTsResponse)
async def validate_ts(request: ValidateTsRequest):
    try:
        log_info(
            "validate_ts_request_received",
            file_name=request.file_name,
            file_extension=request.file_name.split(".")[-1].lower(),
            code_length=len(request.ts_code or ""),
            target_json_length=len(request.target_json_example or ""),
        )

        result = validate_typescript_on_source(
            code=request.ts_code,
            file_name=request.file_name,
            file_base64=request.file_base64,
            target_json_example=request.target_json_example,
        )

        log_info(
            "validate_ts_request_completed",
            is_valid=result.get("is_valid"),
            source_record_count=result.get("source_record_count"),
            output_record_count=result.get("output_record_count"),
        )

        return ValidateTsResponse(status="ok", **result)

    except Exception as ex:
        log_exception("validate_ts_request_failed", ex)
        return JSONResponse(
            status_code=500,
            content={"message": str(ex)},
        )


@api_router.post("/generate-from-example", response_model=GenerateFromExampleResponse)
async def generate_from_example():
    try:
        csv_path = Path("crmData.csv")
        json_path = Path("crm.json")

        log_info(
            "generate_from_example_started",
            csv_exists=csv_path.exists(),
            json_exists=json_path.exists(),
        )

        if not csv_path.exists():
            log_warning("generate_from_example_missing_csv", path=str(csv_path))
            return JSONResponse(status_code=404, content={"message": "crmData.csv not found"})

        if not json_path.exists():
            log_warning("generate_from_example_missing_json", path=str(json_path))
            return JSONResponse(status_code=404, content={"message": "crm.json not found"})

        file_base64 = base64.b64encode(csv_path.read_bytes()).decode("utf-8")
        target_json_example = json.dumps(
            json.loads(json_path.read_text(encoding="utf-8")),
            ensure_ascii=False,
        )

        log_info(
            "generate_from_example_files_loaded",
            file_base64_length=len(file_base64),
            target_json_length=len(target_json_example),
        )

        extracted_preview = build_file_preview(
            file_name="crmData.csv",
            base64file=file_base64,
        )
        target_schema = extract_json_structure(target_json_example)

        log_info(
            "generate_from_example_preview_schema_ready",
            preview_length=len(extracted_preview),
            schema_length=len(target_schema),
        )

        informative, reason = preview_is_informative(extracted_preview)
        if not informative:
            log_warning(
                "generate_from_example_preview_not_informative",
                reason=reason,
            )
            return GenerateFromExampleResponse(
                content="",
                extracted_preview=extracted_preview,
                target_schema=target_schema,
                status="warning",
                valid_ts=False,
                message=reason,
            )

        log_info("generate_from_example_llm_request_started")

        raw_result = chain.invoke(
            {
                "file_name": "crmData.csv",
                "file_extension": "csv",
                "target_schema": target_schema,
                "extracted_preview": extracted_preview,
            }
        )

        log_info(
            "generate_from_example_llm_response_received",
            raw_result_length=len(raw_result or ""),
        )

        normalized_result = normalize_typescript_code(raw_result)
        valid_ts = looks_like_typescript(normalized_result)

        log_info(
            "generate_from_example_llm_response_normalized",
            normalized_length=len(normalized_result or ""),
            valid_ts=valid_ts,
        )

        if not valid_ts:
            log_warning(
                "generate_from_example_typescript_validation_warning",
                message="LLM returned a response that needs manual review.",
            )

        response = GenerateFromExampleResponse(
            content=normalized_result,
            extracted_preview=extracted_preview,
            target_schema=target_schema,
            status="ok" if valid_ts else "warning",
            valid_ts=valid_ts,
            message="" if valid_ts else "LLM returned a response that needs manual review.",
        )

        log_info(
            "generate_from_example_completed",
            status=response.status,
            valid_ts=response.valid_ts,
        )
        return response

    except Exception as ex:
        log_exception("generate_from_example_failed", ex)
        return JSONResponse(
            status_code=500,
            content={"message": str(ex)},
        )