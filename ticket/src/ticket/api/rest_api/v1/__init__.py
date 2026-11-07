from fastapi import APIRouter

from ticket.api.rest_api.v1.ticket.ticket_controller import router as ticket_router
from ticket.api.rest_api.v1.assignment.assignment_controller import router as assignment_router


router = APIRouter()

router.include_router(router=ticket_router, prefix="/ticket")
router.include_router(router=assignment_router, prefix="/assignment")



