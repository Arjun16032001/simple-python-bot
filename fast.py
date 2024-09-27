from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware



# Database setup
DATABASE_URL = "sqlite:///./hotel.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Reservation(Base):
    __tablename__ = "reservations"
    name = Column(String)
    seat_number = Column(String, primary_key=True)

Base.metadata.create_all(bind=engine)

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5005"],  # Replace with the origin where Rasa is running
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods (GET, POST, DELETE, etc.)
#     allow_headers=["*"],  # Allows all headers
# )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ReservationCreate(BaseModel):
    name: str
    seat_number: str

@app.post("/reserve/", response_model=ReservationCreate)
def create_reservation(
    reservation: ReservationCreate, db: Session = Depends(get_db)
):
    # Print incoming data for debugging
    print("Incoming reservation data:", reservation.dict())

    # Check if the seat is already reserved
    existing_reservation = db.query(Reservation).filter_by(seat_number=reservation.seat_number).first()
    if existing_reservation:
        raise HTTPException(status_code=400, detail="Seat is already reserved")

    # Create and add reservation to the database
    new_reservation = Reservation(
        name=reservation.name,
        seat_number=reservation.seat_number
    )
    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)

    return new_reservation

# @app.delete("/cancel/{seat_number}")
# def delete_reservation(seat_number: str, db: Session = Depends(get_db)):
#     print(f"Received request to delete reservation for seat number: {seat_number}")
#     reservation = db.query(Reservation).filter(Reservation.seat_number == seat_number).first()
#     if reservation is None:
#         raise HTTPException(status_code=404, detail="Reservation not found")
#     db.delete(reservation)
#     db.commit()
#     return {"message": "Reservation deleted"}

# @app.get("/reserve/{seat_number}")
# def get_reservation(seat_number: str):
#     db = SessionLocal()
#     reservation = db.query(Reservation).filter(Reservation.seat_number == seat_number).first()
#     if reservation:
#         return {"name": reservation.name, "date": reservation.date, "seat_number": reservation.seat_number}
#     else:
#         raise HTTPException(status_code=404, detail="Reservation not found")
