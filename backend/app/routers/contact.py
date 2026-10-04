from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str


@router.post("/contact", tags=["Contact"])
def submit_contact(form: ContactForm):
    """
    Minimal contact form endpoint.
    Stores contact submissions in logs for now.
    """
    try:
        logger.info(
            "Contact form submission: name=%s, email=%s, subject=%s, message=%s",
            form.name,
            form.email,
            form.subject,
            form.message,
        )
        return {"status": "success", "message": "Contact form submitted successfully"}
    except Exception as exc:
        logger.error("Contact form submission failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to submit contact form")
