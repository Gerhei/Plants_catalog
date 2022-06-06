# Plants catalog
Plants catalog is a website that collects information about various types of plants. There is also a forum dedicated to this topic and a news blog. All the logic of the site is implemented using the Django framework, used by the SQLite DBMS.

## Installing the project locally
If you have a desire to try out this site on your local device, you need to perform the following actions:
1. Install Python interpreter version 3.10.4 and higher.
2. Upload the project using the **git clone** command.
3. In project directories install the necessary dependencies using command **pip3 install -r requirements.txt**.
4. Load fixtures: **python manage.py loaddata plants.json news.json**
5. To start the server, in project directories enter the command **python manage.py runserver** and go to the suggested url.

If you need to enable additional features:
- Using the administrative part of the site -> enter command **python manage.py createsuperuser**. To log in to the administrative part of the site, use the created username and password.
- Password reset for site users -> in the main_app/main_app/settings.py file it is necessary to set your own values of your mail server in the SMTP server settings section.
- To collect new news about plants on the site -> enter the command **python manage.py parse_news**
