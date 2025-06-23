# Personal finances storing and analyzing website

# Description

This project was created during the Software Architecture course. The essence of the project is to effectively control personal financial flows by entering data into the system. Each user will enter data on received and spent money to view the overall picture. The analysis will be available with total expenses, expenses for a certain period (day, week, month, year), saved money, deferred money, borrowed money, creating goals for the month, and budget distribution.

# Technologies

The Personal Finances Storing and Analyzing Website was developed using Python with the Django framework for both the backend and frontend, utilizing simple CSS development. Django handled user authentication, transaction management, and business logic, while also rendering dynamic HTML templates using Django’s built-in Template Engine for the frontend. MySQL served as the database management system, ensuring efficient storage and retrieval of financial data. The application was hosted on an Apache web server, which managed incoming requests and served the application securely. For deployment, Virtual Machines (VMs) were used, providing scalability, system isolation, and efficient resource allocation. This technology stack ensured a reliable, secure, and high-performance platform for managing personal finances.

# How to run the project

To run the project, start by creating virtual machines to host the application. Then install Apache web server and Django framework along with all necessary dependencies such as Python, pip, and required Python packages. After that, import the project code while preserving the existing folder structure. Once the code is in place, apply database migrations using Django’s migration system to set up the required tables. Finally, configure and start the Apache server to serve the Django application.
