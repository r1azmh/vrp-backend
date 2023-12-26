# VRP Solutions - BackEnd
This is a project affiliated with University of Vaasa, Finland.
#### Project Title: [Optimising distribution transport in the food ecosystem](https://www.uwasa.fi/en/elintarvike-ekosysteemi)
#### Principal Investigator: [Professor Petri Helo](https://www.uwasa.fi/en/person/1041808)
This project utilizes the OpenSource VRP Solver, [VRP CLI](https://github.com/reinterpretcat/vrp). The objective is to develop a user-friendly VRP Solver with a straightforward user interface, implementing an efficient algorithm.
## How to install
Before you begin, make sure you have Python 3.9 or 3.10 installed.
1. Install Required Libraries
```bash
# Install Django
pip install django==4.2

# Install django-userforeignkey
pip install django-userforeignkey==0.5.0

# Install VRP CLI
pip install vrp-cli==1.22.1

# Install Pydantic
pip install pydantic==2.3.0
```
2. Clone and Run
* Choose the project directory: Open the Command Prompt and go to the desired location of your computer where you want to download the project.
```shell
cd C:\your-location
```
* Clone the repository to your computer:
```shell
git clone https://github.com/r1azmh/vrp-backend.git
```
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
