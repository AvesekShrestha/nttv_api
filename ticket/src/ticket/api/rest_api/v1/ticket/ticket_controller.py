from fastapi import APIRouter

from ticket.application.ticket.dto.ticket_create_dto import TicketCreateDTO
from ticket.application.ticket.dto.ticket_response_dto import TicketResponseDTO
from ticket.application.ticket.dto.ticket_update_dto import TicketUpdateDTO

router = APIRouter()

router.get("/", response_model=list[TicketResponseDTO])
async def get_all(self) -> list[TicketResponseDTO]: 
    pass

router.get("/{ticket_id}", response_model=TicketResponseDTO)
async def get_by_id(self, ticket_id : str) -> TicketResponseDTO : 
    pass

router.post("/")
async def create(self, payload : TicketCreateDTO) -> TicketResponseDTO :
    pass

router.patch("/{ticket_id}", response_model=TicketResponseDTO)
async def update(self, payload : TicketUpdateDTO) -> TicketResponseDTO : 
    pass

router.delete("/{ticket_id}", response_model=TicketResponseDTO)
async def delete(self, ticket_id : str) -> TicketResponseDTO : 
    pass
