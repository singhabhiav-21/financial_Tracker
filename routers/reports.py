import traceback
from fastapi import APIRouter, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from dependencies import get_current_user
from models.report_models import ReportGenerateRequest
from Visuals.Monthly_Report import (
    get_reports_service, download_report_service,
    generate_monthly_report_service, delete_report_service
)

router = APIRouter(prefix="/api/reports")


@router.get("")
async def get_reports(current_user_id: int = Depends(get_current_user)):
    return await run_in_threadpool(get_reports_service, current_user_id)


@router.get("/download")
async def download_report(month: str, current_user_id: int = Depends(get_current_user)):
    try:
        file_path, filename = await run_in_threadpool(download_report_service, month, current_user_id)
        return FileResponse(path=file_path, filename=filename, media_type='application/pdf')
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_report(data: ReportGenerateRequest, current_user_id: int = Depends(get_current_user)):
    try:
        result = await run_in_threadpool(generate_monthly_report_service, user_id=current_user_id, month=data.month)
        return {"success": True, "message": f"Report generated successfully for {data.month}", **result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{report_id}")
async def delete_report(report_id: int, current_user_id: int = Depends(get_current_user)):
    try:
        result = await run_in_threadpool(delete_report_service, report_id, current_user_id)
        return {"success": True, "message": "Report deleted successfully", **result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")