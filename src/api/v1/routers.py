import base64
import json
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from agent import chain
from api.v1.schemas import (
    GenerateFromExampleResponse,
    GenerateTsRequest,
    GenerateTsResponse,
)
from services.file_preview import build_file_preview
from services.json_schema import extract_json_structure
from services.llm_postprocess import (
    looks_like_typescript,
    normalize_typescript_code,
    preview_is_informative,
)

api_router = APIRouter()


@api_router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "sber-ts-generator",
    }


@api_router.post("/prediction", response_model=GenerateTsResponse)
async def prediction(request: GenerateTsRequest):
    try:
        extracted_preview = build_file_preview(
            file_name=request.file_name,
            base64file=request.file_base64,
        )

        target_schema = extract_json_structure(request.target_json_example)

        informative, reason = preview_is_informative(extracted_preview)
        if not informative:
            return GenerateTsResponse(
                content="",
                extracted_preview=extracted_preview,
                target_schema=target_schema,
                status="warning",
                valid_ts=False,
                raw_content="",
                message=reason,
            )

        raw_result = chain.invoke(
            {
                "file_name": request.file_name,
                "file_extension": request.file_name.split(".")[-1].lower(),
                "target_schema": target_schema,
                "extracted_preview": extracted_preview,
            }
        )

        normalized_result = normalize_typescript_code(raw_result)
        valid_ts = looks_like_typescript(normalized_result)

        return GenerateTsResponse(
            content=normalized_result,
            extracted_preview=extracted_preview,
            target_schema=target_schema,
            status="ok" if valid_ts else "warning",
            valid_ts=valid_ts,
            raw_content=raw_result,
            message="" if valid_ts else "LLM returned a response that needs manual review.",
        )
    except Exception as ex:
        return JSONResponse(
            status_code=500,
            content={"message": str(ex)},
        )


@api_router.post("/generate-from-example", response_model=GenerateFromExampleResponse)
async def generate_from_example():
    try:
        csv_path = Path("crmData.csv")
        json_path = Path("crm.json")

        if not csv_path.exists():
            return JSONResponse(status_code=404, content={"message": "crmData.csv not found"})
        if not json_path.exists():
            return JSONResponse(status_code=404, content={"message": "crm.json not found"})

        file_base64 = base64.b64encode(csv_path.read_bytes()).decode("utf-8")
        target_json_example = json.dumps(
            json.loads(json_path.read_text(encoding="utf-8")),
            ensure_ascii=False,
        )

        extracted_preview = build_file_preview(
            file_name="crmData.csv",
            base64file=file_base64,
        )
        target_schema = extract_json_structure(target_json_example)

        informative, reason = preview_is_informative(extracted_preview)
        if not informative:
            return GenerateFromExampleResponse(
                content="",
                extracted_preview=extracted_preview,
                target_schema=target_schema,
                status="warning",
                valid_ts=False,
                message=reason,
            )

        raw_result = chain.invoke(
            {
                "file_name": "crmData.csv",
                "file_extension": "csv",
                "target_schema": target_schema,
                "extracted_preview": extracted_preview,
            }
        )

        normalized_result = normalize_typescript_code(raw_result)
        valid_ts = looks_like_typescript(normalized_result)

        return GenerateFromExampleResponse(
            content=normalized_result,
            extracted_preview=extracted_preview,
            target_schema=target_schema,
            status="ok" if valid_ts else "warning",
            valid_ts=valid_ts,
            message="" if valid_ts else "LLM returned a response that needs manual review.",
        )
    except Exception as ex:
        return JSONResponse(
            status_code=500,
            content={"message": str(ex)},
        )