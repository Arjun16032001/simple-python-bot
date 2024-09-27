import spacy
import requests

nlp = spacy.load("en_core_web_sm")

intents={
    "greet": ["hi","hello","good morning"],
    "book" : ["book","reserve","buy"],
    "name" : ["name"],
    "seat" : ["seat"]
}

responses={
    "greet": "Hi I am a booking app, how can I help you",
    "book" : "Ok I can take your booking Please tell your name",
    "name" : "What seat do you prefer",
    "seat" : "Thank you for using booking app "

}

user_story = {
    "booking_started": False,
    "name_provided": False,
    "seat_provided": False
}


def read_intent(message):
    doc=nlp(message)
    for token in doc:
        for intent,i in intents.items():
            if token.text in i:
                return intent
    return None

def read_entity(message):
    doc=nlp(message)
    for ent in doc.ents:
        print(f"entity:{ent.text},slot:{ent.label_}")

def extract_seat_number(message):
    """Extract seat number using SpaCy's entity method """
    doc = nlp(message)
    seat_number = None
    if not seat_number:
        for ent in doc.ents:
            if ent.label_ == "CARDINAL":  # SpaCy recognizes numbers as 'CARDINAL'
                seat_number = ent.text
                break
    
    return seat_number

def extract_name(message):   
    doc = nlp(message)
    name = None
    if not name:
        for ent in doc.ents:
            if ent.label_ == "PERSON":  
                name = ent.text
                break
    
    return name

def give_response(message):
    """Generate a response based on the conversation state and intent"""
    global user_story

    intent = read_intent(message)
    
    # if not intent:
    #     return "I didn't get that."

    # Handle the story flow based on the state
    if intent == "greet":
        return responses["greet"]

    # Start the booking process
    if intent == "book" and not user_story["booking_started"]:
        user_story["booking_started"] = True
        return responses["book"]

    # Ask for seat after the name is provided
    if user_story["booking_started"] and not user_story["name_provided"]:
        name = extract_name(message)
        if name:
          user_story["name_provided"] = True
          user_story["name"]=name
          return responses["name"]
        else:
            return "I didn't catch the name. Please provide a name."

    # End the story with seat information
    if user_story["name_provided"] and not user_story["seat_provided"]:
        seat_number = extract_seat_number(message)
        if seat_number:
            user_story["seat_provided"] = True
            user_story["seat_number"]=seat_number
            book(user_story["name"],user_story["seat_number"])
            return responses["seat"].format(seat=seat_number)
        else:
            return "I didn't catch the seat number. Please provide a seat number."

    return "I didn't get that."

def book(name,seat_number):
    response = requests.post("http://127.0.0.1:8000/reserve/", json={
    "name": name,
    "seat_number": seat_number
    })

    if response.status_code == 200:
      print("Your reservation has been successfully made!")
    elif response.status_code == 400:
        print("Sorry, Seat already booked. ")
    else:
        print("Sorry, something went wrong with your reservation.")


if __name__ == "__main__":
    print("Chatbot: Hello ")
    while True:
        user_input = input("user :")
        if user_input=="exit":
            print('Chatbot:bye')
            break
        else:
            read_entity(user_input)
            answer=give_response(user_input)
            print(f"Chatbot:{answer}")
            # book(user_input)
            # doc=nlp(user_input)
            # for ent in doc.ents:
            #   if ent.label_=='PERSON':
            #    book(user_input)