from datetime import datetime as dtdt
from datetime import timedelta
from collections import UserDict
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Телефон має бути 10 символів")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = dtdt.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Неправильний формат дати. Правильний формат ДД.ММ.РРРР")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def delete_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = Phone(new_phone)
                break

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p.value
        return None

    def __str__(self):
        return f"Ім'я контакту: {self.name}, телефон: {'; '.join(str(p) for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def find(self, name):
        return self.data.get(name)


def get_upcoming_birthdays(users):
    upcoming_birthdays = []
    current_date = dtdt.today().date()
    for user in users:
        if user.birthday:
            birthday_this_year = dtdt(
                current_date.year, user.birthday.value.month, user.birthday.value.day
            ).date()
            if birthday_this_year < current_date:
                birthday_this_year = dtdt(
                    current_date.year + 1,
                    user.birthday.value.month,
                    user.birthday.value.day,
                ).date()
            days_until_birthday = (birthday_this_year - current_date).days
            if 0 <= days_until_birthday <= 7:
                if birthday_this_year.weekday() >= 5:
                    birthday_this_year += timedelta(
                        days=(7 - birthday_this_year.weekday())
                    )

                upcoming_birthdays.append(
                    {
                        "Ім'я": user.name.value,
                        "Дата дня народження": birthday_this_year.strftime("%Y.%m.%d"),
                    }
                )

    return upcoming_birthdays


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, IndexError) as e:
            if isinstance(e, KeyError):
                return "Контакт не знайдено."
            elif isinstance(e, ValueError):
                return "Неправильне значення."
            elif isinstance(e, IndexError):
                return "Недостатньо аргументів."

    return inner


def parse_input(user_input):
    tokens = user_input.strip().split(" ")
    command = tokens[0].lower()
    arguments = tokens[1:]
    return command, arguments


@input_error
def add_contact(username, phone, book):
    record = Record(username)
    record.add_phone(phone)
    book.add_record(record)
    return f"Контакт {username} з номером {phone} додано."


@input_error
def change_contact(username, new_phone, book):
    record = book.find(username)
    if record:
        record.edit_phone(record.phones[0].value, new_phone)
        return f"Номер телефону для контакту {username} змінено на {new_phone}."
    else:
        raise KeyError


@input_error
def show_phone(username, book):
    record = book.find(username)
    if record:
        return f"Номер телефону для контакту {username}: {record.phones[0].value}."
    else:
        raise KeyError


@input_error
def show_all_contacts(book):
    if book.data:
        result = "Список контактів:\n"
        for username, record in book.data.items():
            result += f"{record.name.value}: {record.phones[0].value}\n"
        return result
    else:
        return "У вас ще немає збережених контактів."


@input_error
def add_birthday(args, book):
    if len(args) == 2:
        contact_name, birthday = args
        record = book.find(contact_name)
        if record:
            record.add_birthday(birthday)
            return f"День народження додано до {contact_name}."
        else:
            return "Контакт не знайдено."
    else:
        return "Неправильне використання. Напиши ім'я, а потім дату народження."


@input_error
def show_birthday(args, book):
    if len(args) == 1:
        contact_name = args[0]
        record = book.find(contact_name)
        if record and record.birthday:
            return f"{contact_name} має день народження {record.birthday.value.strftime('%d.%m.%Y')}."
        else:
            return "Не знайдено контакт або не вказано день народження."
    else:
        return "Неправильне використання. Введи команду, а потім ім'я."


@input_error
def birthdays(args, book):
    upcoming_birthdays = get_upcoming_birthdays(book.data.values())
    if upcoming_birthdays:
        return f"Найближчі дні народження: {upcoming_birthdays}"
    else:
        return "Найближчих днів народжень немає."


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def main():
    book = load_data()

    print("Вітаю! Це ваш консольний бот-помічник.")
    print(
        "Доступні команди: hello, add, change, phone, all, add-birthday, show-birthday, birthdays, exit"
    )

    while True:
        user_input = input("Введіть команду: ")
        command, arguments = parse_input(user_input)

        if command == "exit" or command == "close":
            save_data(book)
            print("До зустрічі!")
            break
        elif command == "hello":
            print("Як я можу допомогти?")
        elif command == "add":
            if len(arguments) == 2:
                result = add_contact(arguments[0], arguments[1], book)
                print(result)
            else:
                print(
                    "Неправильне використання команди add. Введіть ім'я та номер телефону."
                )
        elif command == "change":
            if len(arguments) == 2:
                result = change_contact(arguments[0], arguments[1], book)
                print(result)
            else:
                print(
                    "Неправильне використання команди change. Введіть ім'я та новий номер телефону."
                )
        elif command == "phone":
            if len(arguments) == 1:
                result = show_phone(arguments[0], book)
                print(result)
            else:
                print("Неправильне використання команди phone. Введіть ім'я контакту.")
        elif command == "all":
            result = show_all_contacts(book)
            print(result)
        elif command == "add-birthday":
            result = add_birthday(arguments, book)
            print(result)
        elif command == "show-birthday":
            result = show_birthday(arguments, book)
            print(result)
        elif command == "birthdays":
            result = birthdays(arguments, book)
            print(result)
        else:
            print("Невідома команда. Спробуйте ще раз.")


if __name__ == "__main__":
    main()
