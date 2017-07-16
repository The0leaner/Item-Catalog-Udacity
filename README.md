# Item-Catalog-Udacity
udacity project Item Catalog App

## Tips to Run Project

### Set up a Google Plus auth application.
1. go to [google](https://console.developers.google.com/project) and login with Google.
2. Create a new project
3. Select "API's and Auth-> Credentials-> Create a new OAuth client ID" from the project menu
4. Select Web Application
5. follow the tips given by google

### Launching the Virtual Machine:

  1. Launch the Vagrant VM inside Vagrant sub-directory in the downloaded repository using command and ssh connect to it:
  
  ```
    $ vagrant up
  ```
  ```
    $ vagrant ssh
  ```
  2. Change directory to /vagrant/catlog (mkdir it by yourself).
  

### Setup the Database 
 
  1. create the database with the categories defined in that "db_setup.py". 
  ```
    $ python db_setup.py
  ```
   2. initial the data of the categories from [wiki](https://www.wikipedia.org/). (optional)
  ```
    $ python intialdb.py
  ```

### Start the Server
  After doing all that run the following command:
  ```
    $ python application.py
  ```

### JSON End Points

The home page, category list page and item details page show thier JSON end points, which can be created by appending `.json` to the URL

- For the home page, use `http://localhost:8000/index.json`
- For items in a particular category use `http://localhost:8000/catalog/CategoryName.json`
- For a single item, use `http://localhost:8000/catalog/CategoryName/ItemName.json`
