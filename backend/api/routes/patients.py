"""Patient management endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.models.schemas import (
    PatientCreate, 
    PatientResponse, 
    PatientUpdate,
    PatientWithOperations,
    PatientOperationStats,
    PatientFilter
)
from backend.services.patient_service import PatientService
from backend.services.operation_service import OperationService

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", response_model=PatientResponse, status_code=201)
async def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """Create a new patient."""
    # Check for duplicate patients (same sex and birth_date - basic check)
    existing = PatientService.find_duplicate(db, patient.sex, patient.birth_date)
    if existing:
        raise HTTPException(
            status_code=409, 
            detail=f"Similar patient already exists (ID: {existing.id})"
        )
    
    created_patient = PatientService.create(
        db,
        sex=patient.sex,
        birth_date=patient.birth_date
    )
    return created_patient


@router.get("", response_model=List[PatientResponse])
async def list_patients(
    filters: PatientFilter = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List patients with optional filters:
    - sex: filter by sex
    - age_min/age_max: filter by age range
    - has_operations: filter patients with/without operations
    - search: search by ID or partial matches
    """
    patients = PatientService.list_filtered(
        db,
        sex=filters.sex,
        age_min=filters.age_min,
        age_max=filters.age_max,
        has_operations=filters.has_operations,
        search=filters.search,
        skip=skip,
        limit=limit
    )
    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """Get patient by ID."""
    patient = PatientService.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int, 
    patient_update: PatientUpdate, 
    db: Session = Depends(get_db)
):
    """Update patient information."""
    patient = PatientService.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # If updating sex/birth_date, check for duplicates
    if patient_update.sex or patient_update.birth_date:
        check_sex = patient_update.sex or patient.sex
        check_birth = patient_update.birth_date or patient.birth_date
        existing = PatientService.find_duplicate(db, check_sex, check_birth, exclude_id=patient_id)
        if existing:
            raise HTTPException(
                status_code=409, 
                detail=f"Similar patient already exists (ID: {existing.id})"
            )
    
    updated = PatientService.update(
        db, 
        patient_id=patient_id,
        **patient_update.model_dump(exclude_unset=True)
    )
    return updated


@router.delete("/{patient_id}", status_code=204)
async def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """Delete a patient and all associated data (cascading)."""
    patient = PatientService.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Check if patient has operations with predictions
    patient_with_ops = PatientService.get_with_operations(db, patient_id)
    if patient_with_ops:
        for operation in patient_with_ops.operations:
            if operation.predictions:
                raise HTTPException(
                    status_code=409,
                    detail=f"Cannot delete patient: operation #{operation.id} has predictions. "
                           "Remove predictions or use force=true parameter."
                )
    
    PatientService.delete(db, patient_id)


@router.delete("/{patient_id}/force", status_code=204)
async def force_delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Force delete a patient and ALL associated data including predictions.
    WARNING: This is irreversible!
    """
    patient = PatientService.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    PatientService.force_delete(db, patient_id)


@router.get("/{patient_id}/operations", response_model=PatientWithOperations)
async def get_patient_operations(
    patient_id: int,
    operation_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get patient with all their operations."""
    patient = PatientService.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient_with_ops = PatientService.get_with_operations(
        db, 
        patient_id,
        operation_type=operation_type
    )
    return patient_with_ops


@router.get("/{patient_id}/stats", response_model=PatientOperationStats)
async def get_patient_stats(patient_id: int, db: Session = Depends(get_db)):
    """Get comprehensive statistics for a patient."""
    patient = PatientService.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return PatientService.get_stats(db, patient_id)


@router.get("/stats/age-distribution")
async def get_age_distribution(db: Session = Depends(get_db)):
    """Get age distribution of patients with operations."""
    return PatientService.get_age_distribution(db)


@router.post("/{patient_id}/merge/{target_patient_id}", status_code=200)
async def merge_patients(
    patient_id: int, 
    target_patient_id: int, 
    db: Session = Depends(get_db)
):
    """
    Merge source patient into target patient.
    All operations from source patient are moved to target patient.
    Source patient is deleted after merge.
    """
    if patient_id == target_patient_id:
        raise HTTPException(status_code=400, detail="Cannot merge patient with itself")
    
    source = PatientService.get(db, patient_id)
    target = PatientService.get(db, target_patient_id)
    
    if not source:
        raise HTTPException(status_code=404, detail=f"Source patient #{patient_id} not found")
    if not target:
        raise HTTPException(status_code=404, detail=f"Target patient #{target_patient_id} not found")
    
    merged_ops_count = PatientService.merge_patients(db, patient_id, target_patient_id)
    
    return {
        "message": f"Patient #{patient_id} merged into #{target_patient_id}",
        "moved_operations": merged_ops_count,
        "source_deleted": True
    }