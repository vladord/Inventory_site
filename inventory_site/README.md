Flask==3.1.1
Flask-RESTful==0.3.10
customtkinter==5.2.2
requests==2.32.4

If files don't exist:
Create file inventory.log in folder ./data/
Create file inventory.csv in folder ./data/ with next columns:
id,serial,partnumber,type,model,location,last_user,user,lastupdate,comment

To Build:
pyinstaller --onefile --noconsole your_script_name.py


