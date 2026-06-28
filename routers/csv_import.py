import re
import os
import tempfile
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from dependencies import get_current_user
from databaseDAO.transaction.importcsv import bankImporter

router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'.csv'}
ALLOWED_MIME_TYPES = {'text/csv', 'application/vnd.ms-excel', 'text/plain', 'application/csv'}


def validate_file_security(file: UploadFile) -> tuple[bool, str]:
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, "Invalid file type. Only CSV files allowed."

    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        return False, f"Invalid MIME type: {file.content_type}"

    suspicious_chars = ['..', '\0', '<', '>', ':', '"', '|', '?', '*']
    if any(char in file.filename for char in suspicious_chars):
        return False, "Invalid filename format"

    if len(file.filename) > 255:
        return False, "Filename too long"

    return True, ""


def normalize_column_name(col: str) -> str:
    return re.sub(r'[\s_-]', '', col.lower().strip())


def validate_csv_columns(header_line: str) -> tuple[bool, str]:
    header_cols = re.split(r'[,;\t]', header_line.lower())
    normalized_cols = [normalize_column_name(col.strip('"\'')) for col in header_cols]

    required = ['valuedate', 'text', 'amount']
    missing = [req for req in required if not any(req in norm or norm in req for norm in normalized_cols)]

    if missing:
        return False, f"Missing required columns: {', '.join(missing)}. Found: {', '.join(header_cols[:5])}"

    return True, ""


@router.post("/import-csv")
async def import_csv_transactions(
    file: UploadFile = File(...),
    current_user_id: int = Depends(get_current_user)
):
    is_valid, error_msg = validate_file_security(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    temp_file_path = None

    try:
        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024 * 1024):.1f} MB")
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        if b'\x00' in content:
            raise HTTPException(status_code=400, detail="File contains invalid characters")

        try:
            text_content = content.decode('utf-8-sig')
        except UnicodeDecodeError:
            try:
                text_content = content.decode('latin-1')
            except UnicodeDecodeError:
                raise HTTPException(status_code=400, detail="Unable to decode file. Please ensure it's a valid CSV.")

        lines = [line for line in text_content.split('\n') if line.strip()]
        if len(lines) < 2:
            raise HTTPException(status_code=400, detail="CSV file is too short or empty")

        # Strip outer quotes from lines if present
        fixed_lines = []
        for line in lines:
            if line.startswith('"') and line.endswith('"') and line.count('"') == 2:
                fixed_lines.append(line[1:-1])
            else:
                fixed_lines.append(line)

        text_content = '\n'.join(fixed_lines)

        is_valid, error_msg = validate_csv_columns(fixed_lines[0])
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(text_content)
            temp_file_path = temp_file.name

        importer = bankImporter(user_id=current_user_id, default_category_id=1)
        importer.import_csv(temp_file_path)

        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

        return JSONResponse(status_code=200, content={
            "message": "Import completed successfully",
            "imported": importer.imported_count,
            "duplicates": importer.duplicate_count,
            "total": importer.imported_count + importer.duplicate_count,
            "user_id": current_user_id
        })

    except HTTPException:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass
        raise

    except Exception as e:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    finally:
        await file.close()