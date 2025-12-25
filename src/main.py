import csv
import json
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
import os


# Reads data from CSV file and turns it into a dictionary
def csv_reader(file_name):
    list_data = []
    # opening the CSV file
    with open(file_name, mode='r') as file:
        # Reading the CSV file
        csv_file = csv.DictReader(file)
        # displaying the contents of the CSV file
        for lines in csv_file:
            list_data.append(lines)
        return list_data


# After shuffling the lists, checks if any the gifter and giftee are the same person and changes the order
def no_two_pairs(giftees, gifters):
    for i in range(0, len(giftees)):
        if giftees[i]['Name'] == gifters[i]['Name']:
            if i + 1 == len(giftees):
                temp = gifters[0]
                gifters[0] = gifters[i]
                gifters[i] = temp
            else:
                temp = gifters[i + 1]
                gifters[i + 1] = gifters[i]
                gifters[i] = temp
            return no_two_pairs(giftees, gifters)
    return gifters


# Verifies there are no matches, i.e. gifteer and giftee are the same person
def verify_no_matches(gifters, giftees):
    for i in range(0, len(gifters)):
        if gifters[i]['Name'] == giftees[i]['Name']:
            return False
    return True


def matcher(people, person_filter: dict = None):
    while True:
        matches = []
        giftees = people.copy()
        random.shuffle(giftees)
        gifters = people.copy()
        random.shuffle(gifters)
        for i in range(0, len(people)):
            skip = False
            if gifters[i]["Name"] == giftees[i]["Name"]:
                print(f"Same person: {gifters[i]['Name']} -> {giftees[i]['Name']}")
                break
            for person in person_filter:
                if (person is not None and gifters[i]["Email"] in person.keys() and giftees[i]["Email"] in
                        person[gifters[i]["Email"]]):
                    print(f"Person Filter: {gifters[i]['Email']} -> {giftees[i]['Email']}")
                    skip = True
                    break
            if skip:
                break
            matches.append({"Gifter": {"Name": gifters[i]["Name"], "Email": gifters[i]["Email"]},
                            "Giftee": {"Name": giftees[i]["Name"],
                                       "Gifts": [giftees[i]["Amazon link to Gift #1 ($30 max)"],
                                                 giftees[i]["Amazon link to Gift #2 ($30 max)"],
                                                 giftees[i]["Amazon link to Gift #3 ($30 max)"]]}})
        if len(matches) == len(people):
            break
    return matches


def send_email(secret_santa, debug):
    sender_email = os.getenv("SMTP_SENDER_EMAIL")
    receiver_email = secret_santa['Gifter']['Email']
    password = os.getenv("SMTP_PASSWORD")
    message = MIMEMultipart("alternative")
    message["Subject"] = "Your Secret Santa has Arrived!"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"""
    Hello {secret_santa['Gifter']['Name']},
    You are shopping for {secret_santa['Giftee']['Name']}.
    There requested gists are
    1. {secret_santa['Giftee']['Gifts'][0]}
    2. {secret_santa['Giftee']['Gifts'][1]}
    3. {secret_santa['Giftee']['Gifts'][2]}
    Please let me know if you have any questions.
    Love, Jack
    """

    html = f"""\
    <html>
        <body>
            <p> Hello {secret_santa['Gifter']['Name']},<br>
                You are shopping for {secret_santa['Giftee']['Name']}.<br>
                There requested gifts are<br><br>
                1. <a href={secret_santa['Giftee']['Gifts'][0]}>{secret_santa['Giftee']['Gifts'][0]}</a><br>
                2. <a href={secret_santa['Giftee']['Gifts'][1]}>{secret_santa['Giftee']['Gifts'][1]}</a><br> 
                3. <a href={secret_santa['Giftee']['Gifts'][2]}>{secret_santa['Giftee']['Gifts'][2]}</a><br> 
                <br>
                Please let me know if you have any questions.<br>
                Love, Jack
            </p>
        </body>
    </html>
    """
    print(f"Sending email to {secret_santa['Gifter']['Name']} -> {message['To']}")
    if not debug:
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)
        with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as server:
            server.starttls()
            server.login(os.getenv("SMTP_USERNAME"), password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )
    else:
        print(text)


def writer(secret_santa):
    with open('secret-santa.json', 'w') as convert_file:
        convert_file.write(json.dumps(secret_santa))


# Main function that runs the program
def main():
    debug = True
    csv_file = input("Provide Full path to CSV file: ")
    debug_question = input("Enable debug mode (Y/n): ")
    if debug_question.lower() == "no" or debug_question.lower() == "n":
        debug = False
    gifters = csv_reader(csv_file)
    giftees = gifters.copy()
    random.shuffle(giftees)
    gifters = no_two_pairs(giftees, gifters)
    if not verify_no_matches(gifters, giftees):
        print("There is at least 1 match!")
        exit(1)
    secret_santa = matcher(gifters)
    writer(secret_santa)
    for i in range(0, len(giftees)):
        send_email(secret_santa[i], debug)
    exit(0)

if __name__ == '__main__':
    load_dotenv()
    main()
