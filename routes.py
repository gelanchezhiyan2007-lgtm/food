from typing import Optional, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from ai_core.gemini_generator import GeminiDocumentGenerator
from utils.text_sanitizer import sanitize_text
from utils.formatters import format_html_preview
import database

router = APIRouter(prefix="", tags=["Legal Document Generation & History"])
generator = GeminiDocumentGenerator()

class DocumentRequest(BaseModel):
    document_type: str = Field(..., example="Employment Contract", description="Type of legal document")
    parties: str = Field(..., example="TechNova Inc. (Employer), Jane Doe (Employee)", description="Names and roles of involved parties")
    terms: str = Field(..., example="Salary $120,000/yr; 15 days paid leave; Confidentiality required", description="Semicolon separated list of clauses/terms")
    dates: str = Field(..., example="October 15, 2026", description="Effective date of the document")
    custom_instructions: Optional[str] = Field(None, example="Include non-compete clause for 1 year within North America", description="Optional additional legal preferences")

class DocumentResponse(BaseModel):
    status: str
    id: Optional[int] = None
    document_type: str
    parties: str
    effective_date: str
    raw_content: str
    sanitized_content: str
    html_preview: str

@router.post("/generate", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
async def generate_document(req: DocumentRequest):
    """
    POST /generate endpoint:
    Accepts JSON input, calls Gemini AI model, sanitizes text, saves record into SQLite database,
    and returns document content with HTML preview and generated DB ID.
    """
    if not req.document_type or not req.parties:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="document_type and parties fields are required."
        )

    try:
        raw_text = generator.generate_document(
            document_type=req.document_type,
            parties=req.parties,
            terms=req.terms,
            dates=req.dates,
            custom_instructions=req.custom_instructions
        )

        sanitized = sanitize_text(raw_text)
        html_preview = format_html_preview(sanitized, doc_type=req.document_type)

        # Save generated document to SQLite Database
        doc_id = database.save_document(
            document_type=req.document_type,
            parties=req.parties,
            terms=req.terms,
            effective_date=req.dates,
            custom_instructions=req.custom_instructions or "",
            content=sanitized
        )

        return DocumentResponse(
            status="success",
            id=doc_id,
            document_type=req.document_type,
            parties=req.parties,
            effective_date=req.dates,
            raw_content=raw_text,
            sanitized_content=sanitized,
            html_preview=html_preview
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document generation failed: {str(e)}"
        )

@router.get("/history", status_code=status.HTTP_200_OK)
async def get_history():
    """Retrieves all saved legal documents from SQLite database."""
    try:
        docs = database.get_all_documents()
        return {"status": "success", "count": len(docs), "documents": docs}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch document history: {str(e)}"
        )

@router.get("/history/{doc_id}", status_code=status.HTTP_200_OK)
async def get_history_by_id(doc_id: int):
    """Retrieves a specific document from SQLite database by ID."""
    doc = database.get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    html_preview = format_html_preview(doc["content"], doc_type=doc["document_type"])
    return {"status": "success", "document": doc, "html_preview": html_preview}

@router.delete("/history/{doc_id}", status_code=status.HTTP_200_OK)
async def delete_history_by_id(doc_id: int):
    """Deletes a document from SQLite database history."""
    success = database.delete_document_by_id(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "success", "message": f"Document ID {doc_id} deleted successfully"}
