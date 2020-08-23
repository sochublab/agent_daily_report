import os
from os.path import isfile, join

from django.http import HttpResponse
from django.shortcuts import render
from .forms import CreateNewList
import zipfile
import json
import datetime
import re
from collections import Counter
import pandas as pd

dir_path = os.path.dirname(os.path.realpath(__file__))
tmploc = f'{dir_path}/uploads/tmp/'


def index(response):
    return render(response, "main/home.html")


def v1(response):
    return HttpResponse("<h3>Welcome to V1</h3>")


def report(request):
    # Delete all from uploads folder
    upath = f'{dir_path}/uploads'
    filelist = [f for f in os.listdir(upath) if isfile(join(upath, f))]
    print(filelist)
    for f in filelist:
        os.remove(os.path.join(upath, f))
    htmldata = "<div class='container'><p></p>"
    if request.method == 'POST':
        form = CreateNewList(request.POST, request.FILES)
        if form.is_valid():
            formdata = request.POST.dict()
            n = formdata.get('name')
            f = formdata.get('uploadfile')
            d = formdata.get('datefield')
            handle_uploaded_file(request.FILES['uploadfile'], d)
            print(n, d, f)
            htmldata = generate_report(d)
    else:
        form = CreateNewList()
    return render(request, "main/report.html", {"form": form, 'html_table': htmldata})


def handle_uploaded_file(f, filename):
    with open(f'{dir_path}/uploads/{filename}.zip', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def makeValidJSON():
    # Get the file extracted in tmp folder
    filelist = [f for f in os.listdir(tmploc)]
    firstfile = filelist[0]

    input_file = f'{dir_path}/uploads/tmp/{firstfile}'
    output_file = f'{dir_path}/uploads/exportfile.json'

    with open(input_file, 'r') as all_input_file_lines:
        all_input_file_lines.readline()

        all_lines_with_comma = str()

        for line in all_input_file_lines:
            all_lines_with_comma += line[:-1] + ",\n"

    with open(output_file, 'w+') as write_output_file:
        write_output_file.writelines('{"tickets":[' + '\n' + all_lines_with_comma[:-3] + "\n}]}")


def generate_report(current_date):
    # Delete all files in tmp folder then only extract the zip file there.
    filelist = [f for f in os.listdir(tmploc)]
    for f in filelist:
        os.remove(os.path.join(tmploc, f))
    # All files removed
    with zipfile.ZipFile(f'{dir_path}/uploads/{current_date}.zip', 'r') as zip_ref:
        zip_ref.extractall(tmploc)  # Extract in tmp folder for now.
    print("Zip Extracted")
    makeValidJSON()
    # open the json file and read it
    exportfilepath = f'{dir_path}/uploads/exportfile.json'
    # Opening JSON file
    f = open(exportfilepath, 'r')
    # This date needs to be from Tkinter and dynamic. May be format it as variable
    COMMENT_DATE = current_date

    # On second thought may be this needs to be webapp
    agent_name_map = {
        '//samir': 'Supesh Basnet',
        '//priya': 'Priyanka Karanjit',
        '//raja': 'Rashmi Napit',
        '//sonu': 'Pratima Dewan',
        '//dipa': 'Dipina Shrestha',
        '//kiran': "Pragati Das",
        '//dev': 'Bibidh Ghimire',
        '//binod': 'Manorama Koirala',
        '//sima': 'Sabina Dhakal',
        '//ami': 'Amina Rana',
        '//abhi': 'Sharmila Parajuli',
        '//prem': 'Dipendra',
        '//anu': 'Kiran',
        '//isha': 'Sagar',
        '//sara': 'Sapana',
        '//gopi': 'Raghu',
        '//suba': 'Shiva',
        '//samar': 'Suzit',
        '//eva': 'Avanthi',
    }

    # returns JSON object as
    # a dictionary
    data = json.load(f)
    agent_name = []
    # We might need to update the variables as needed
    invalid_names = ['//www', None, '//maps', '//youtube', '//youtu', '//payment', '//twitter', '//t', '//bit']
    alltickets = data['tickets']
    for ticket in alltickets:
        for comment in ticket['comments']:
            created_at = comment['created_at']
            plain_body = comment['plain_body'].replace('\n', '')
            # sender = comment['via']['source']['from']['name']
            d1 = datetime.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")
            # print(d1, sender, plain_body)
            if d1 == COMMENT_DATE:
                # print(d1, plain_body)
                try:
                    x = re.search(r"[/][/][a-z]+", plain_body.lower())
                    # print(x.group())
                    agent_name.append(x.group())
                except:
                    x = re.search(r"[/][/][a-z]+", plain_body.lower())
                    agent_name.append(x)

    # Remove invalid names from the final list of agents
    agents = [agent for agent in agent_name if agent not in invalid_names]
    # print(agents)
    print(len(agents))
    d = Counter(agents)
    df = pd.DataFrame.from_dict(d, orient='index').reset_index()
    df = df.rename(columns={'index': 'Nick Name', 0: 'Replies'})
    df['Full Name'] = df['Nick Name'].map(agent_name_map)
    column_titles = ['Full Name', 'Nick Name', 'Replies']
    df = df.reindex(columns=column_titles)
    df = df.sort_values(['Replies', 'Full Name'], ascending=[0, 1])
    # df.to_csv('agentreport.csv', index=False)
    # print(df)
    return df.to_html(classes=["table-bordered", "table-striped", "table-hover"], index=False)
