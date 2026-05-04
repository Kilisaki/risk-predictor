"""Operation management endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.models.schemas import (
    OperationCreate, 
    OperationResponse, 
    OperationWithClinicalData,
    OperationWithPrediction,
    OperationFilter,
    OperationUpdate
)
from backend.services.patient_service import PatientService
from backend.services.operation_service import OperationService

router = APIRouter(prefix="/operations", tags=["operations"])


@router.post("", response_model=OperationResponse, status_code=201)
async def create_operation(operation: OperationCreate, db: Session = Depends(get_db)):
    """Create a new operation."""
    # Verify patient exists
    patient = PatientService.get(db, operation.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Check for duplicate operation
    existing = OperationService.get_by_patient_and_date(
        db, 
        patient_id=operation.patient_id, 
        operation_date=operation.date,
        operation_type=operation.type
    )
    if existing:
        raise HTTPException(
            status_code=409, 
            detail="Operation of this type already exists for this patient on this date"
        )
    
    created_operation = OperationService.create(
        db,
        patient_id=operation.patient_id,
        operation_type=operation.type,
        date_=operation.date
    )
    return created_operation


@router.get("", response_model=List[OperationResponse])
async def list_operations(
    filters: OperationFilter = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List operations with optional filters:
    - patient_id: filter by patient
    - type: filter by operation type
    - date_from, date_to: date range
    - has_predictions: filter operations with/without predictions
    """
    operations = OperationService.list_filtered(
        db,
        patient_id=filters.patient_id,
        operation_type=filters.type,
        date_from=filters.date_from,
        date_to=filters.date_to,
        has_predictions=filters.has_predictions,
        skip=skip,
        limit=limit
    )
    return operations


@router.get("/{operation_id}", response_model=OperationResponse)
async def get_operation(operation_id: int, db: Session = Depends(get_db)):
    """Get operation by ID."""
    operation = OperationService.get(db, operation_id)
    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")
    return operation


@router.get("/{operation_id}/clinical-data", response_model=OperationWithClinicalData)
async def get_operation_with_clinical_data(operation_id: int, db: Session = Depends(get_db)):
    """Get operation with associated clinical data."""
    operation = OperationService.get_with_clinical_data(db, operation_id)
    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")
    if not operation.clinical_data:
        raise HTTPException(status_code=404, detail="No clinical data found for this operation")
    return operation


@router.get("/{operation_id}/prediction", response_model=OperationWithPrediction)
async def get_operation_with_prediction(operation_id: int, db: Session = Depends(get_db)):
    """Get operation with latest prediction."""
    operation = OperationService.get_with_predictions(db, operation_id)
    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")
    if not operation.predictions:
        raise HTTPException(status_code=404, detail="No predictions found for this operation")
    return operation


@router.put("/{operation_id}", response_model=OperationResponse)
async def update_operation(
    operation_id: int, 
    operation_update: OperationUpdate, 
    db: Session = Depends(get_db)
):
    """Update operation details."""
    operation = OperationService.get(db, operation_id)
    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    updated = OperationService.update(
        db, 
        operation_id=operation_id,
        **operation_update.model_dump(exclude_unset=True)
    )
    return updated


@router.delete("/{operation_id}", status_code=204)
async def delete_operation(operation_id: int, db: Session = Depends(get_db)):
    """Delete operation and all associated data (clinical data, predictions)."""
    operation = OperationService.get(db, operation_id)
    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    # Check if operation has predictions
    if operation.predictions:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete operation with predictions. Remove predictions first."
        )
    
    OperationService.delete(db, operation_id)


@router.get("/patient/{patient_id}", response_model=List[OperationResponse])
async def get_patient_operations(
    patient_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all operations for a specific patient."""
    # Verify patient exists
    patient = PatientService.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return OperationService.get_by_patient(db, patient_id, skip=skip, limit=limit)


@router.get("/stats/summary")
async def get_operations_summary(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get operations summary statistics.
    Returns count by type, risk distribution, etc.
    """
    return OperationService.get_summary_stats(db, date_from=date_from, date_to=date_to)