import csv
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/reports", tags=["reports"])

REPORTS_DIR = Path(r"C:\PythonProject\reports")


@router.get("/final")
def list_final_reports():
    if not REPORTS_DIR.exists():
        return []

    files = []

    for file in REPORTS_DIR.glob("*.csv"):
        stat = file.stat()

        files.append({
            "filename": file.name,
            "size": stat.st_size,
            "created_at": stat.st_ctime,
            "modified_at": stat.st_mtime,
        })

    files.sort(key=lambda x: x["modified_at"], reverse=True)

    return files


@router.get("/final/{filename}/preview")
def preview_final_report(filename: str):
    file_path = REPORTS_DIR / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Rapport introuvable")

    if file_path.suffix.lower() != ".csv":
        raise HTTPException(status_code=400, detail="Type de fichier non autorisé")

    rows = []

    try:
        with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                rows.append(row)

    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1", newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                rows.append(row)

    return {
        "filename": filename,
        "rows": rows
    }


@router.get("/final/{filename}")
def download_final_report(filename: str):
    file_path = REPORTS_DIR / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Rapport introuvable")

    if file_path.suffix.lower() != ".csv":
        raise HTTPException(status_code=400, detail="Type de fichier non autorisé")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="text/csv"
    )