from collections import UserDict, defaultdict
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value.strip():
            raise ValueError("Name cannot be empty.")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Invalid phone number. Please enter 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid date format. Please use DD.MM.YYYY.")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                if len(new_phone) != 10:
                    raise ValueError("Invalid phone number. Please enter 10 digits.")
                phone.value = new_phone

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = '; '.join(str(phone) for phone in self.phones)
        birthday_str = str(self.birthday) if self.birthday else "No birthday"
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_birthdays_per_week(self):
        birthdays_by_day = defaultdict(list)
        today = datetime.today().date()
        next_week = today + timedelta(days=7)
    
        for record in self.data.values():
            if record.birthday:
                name = record.name.value
                birthday = datetime.strptime(record.birthday.value, '%d.%m.%Y').date()
                birthday_this_year = birthday.replace(year=today.year)
            
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                delta_days = (birthday_this_year - today).days
                if delta_days < 7:
                    day_of_week = (today + timedelta(days = delta_days)).strftime("%A")
                    if day_of_week in ["Saturday", "Sunday"]:
                        day_of_week = "Monday"
                    birthdays_by_day[day_of_week].append(name)     
        return birthdays_by_day


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone 10 digits please.If date Please use DD.MM.YYYY"
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Invalid command format."
    return inner

@input_error
def add_contact(args, book):
    name, phone = args
    try:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."
    except ValueError as e:
        return str(e)

@input_error
def change_contact(args, book):
    name, new_phone = args
    record = book.find(name)
    if record:
        try:
            record.edit_phone(record.phones[0].value, new_phone)
            return "Contact updated."
        except ValueError as e:
            return str(e)
   
@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record is not None:
        if record.phones:
            return record.phones[0].value
        else:
            return "No phone number set for this contact."
    else:
        raise KeyError("Contact not found.")

@input_error
def show_all(book):
    if not book.data:
        return "Your address book is empty."
    contact_list = "\n".join(str(record) for record in book.data.values())
    return contact_list

@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        try:
            record.add_birthday(birthday)
            return "Birthday added."
        except ValueError as e:
            return str(e) 
    else:
        raise KeyError("Contact not found.")

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        if record.birthday:
            return record.birthday.value
        else:
            return "No birthday set for this contact."
    else:
        raise KeyError("Contact not found.")

def main():
    book = AddressBook()
    print("Welcome to the address book bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Goodbye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            result = show_phone(args, book)
            if isinstance(result, str):
                print(result)
            else:
                print("Phone: " + result)
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            result = show_birthday(args, book)
            if isinstance(result, str):
                print(result)
        elif command == "birthdays":
            birthdays = book.get_birthdays_per_week()
            for day, names in birthdays.items():
                if names:
                    print(f"{day}: {', '.join(names)}")
        else:
            print("Invalid command.")
            
if __name__ == "__main__":
    main()