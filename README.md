# VRP Solutions - BackEnd
This is a project affiliated with University of Vaasa, Finland.
#### Project Title: [Optimising distribution transport in the food ecosystem](https://www.uwasa.fi/en/elintarvike-ekosysteemi)
#### Principal Investigator: [Professor Petri Helo](https://www.uwasa.fi/en/person/1041808)
This project utilizes the OpenSource VRP Solver, [VRP CLI](https://github.com/reinterpretcat/vrp). The objective is to develop a user-friendly VRP Solver with a straightforward user interface, implementing an efficient algorithm.
## How to install
Before you begin, make sure you have Python 3.9 or 3.10 installed.
1. Clone the Repository
* Choose the project directory: Open the Command Prompt and go to the desired location of your computer where you want to download the project.
```shell
cd C:\your-location
```
* Clone the repository to your computer:
```shell
git clone https://github.com/r1azmh/vrp-backend.git
```
2. Install Required Libraries
```shell
cd C:\your-location\vrp-backend
```
```bash
# Install all the required libraries
pip install -r requirements.txt
```
3. Set up Routing Matrix Generator

i. Go to the openrouteservice website using the following link and generate an API key.
[Link](https://openrouteservice.org/dev/)

ii. Go to 
```shell
cd C:\your-location\vrp-backend\base\vrp_extra\utils.py
```
 then replace MYKEY with your API key.
```shell
client = ors.Client(key='MYKEY')
```
4. Make Migrations
* Go to comand prompt and write the following comands.
```bash
python manage.py makemigrations
```
```bash
python manage.py migrate
```
5. Run the Solver
* Run the Django development server:
```shell
python manage.py runserver
```
## How to Use
1. Initiate a New Work
2. Add Jobs
3. Add Vehicles
4. Run the Solver to get the Solution
## Contact

In case of any issues or inquiries, please contact us at [riaz.mahmud@uwasa.fi](mailto:riaz.mahmud@uwasa.fi).
