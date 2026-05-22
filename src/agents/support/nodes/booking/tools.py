from langchain_core.tools import tool


@tool("book_appointment", description="Book a medical appointment for a given date, time, doctor and patient")
def book_appointment(date : str, time : str, doctor : str, patient : str):
    return f"Appointment booked for {date} at {time} with {doctor} for {patient}!"


@tool("get_appointment_availability", description="Get the availability for a medical appointment for given date, time and doctor")
def get_appointment_availability(date : str, time : str, doctor : str):
    return f"""
    The available slots for the {doctor} are : 
    - Monday : 10:00 - 15:00
    - Wednesday : 08:00 - 14:00
    - Thursday : 11:00 - 16:00
    - Friday : 07:00 - 14:00
    """


tools = [book_appointment, get_appointment_availability]