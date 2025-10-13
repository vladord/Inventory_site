from flask import Flask, render_template, jsonify, make_response, send_file
from flask_restful import reqparse, abort, Api, Resource
import csv
import logging
import os
class StudentList(Resource):
    def __init__(self):
        self.csv_file = './data/inventory.csv'
        self.csv_file_columns =["id",
                                "serial",
                                "partnumber",
                                "type",
                                "model",
                                "location",
                                "last_user",
                                "user",
                                "lastupdate",
                                "comment"]
        self.history_file = './data/history.csv'
        self.log_file = './data/inventory.log'

    def log_action(self, user, action):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M:%S',
                            filename= self.log_file,
                            filemode='a')

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger().addHandler(console)
        logger = logging.getLogger(f'{user}')
        logger.info(f"{action}")
        return
  
    def csv_to_list(self):
        data = []
        with open(self.csv_file, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(dict(row))
        return data
    
    def list_to_csv(self, data):
        with open(self.csv_file, "w", newline="", encoding="utf-8") as f:
            fieldnames = self.csv_file_columns
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        return
    
    def find_entry(self, key, value):
        return_value = []

        for row in self.csv_to_list():
            if str(row[key]) == str(value):
                return_value.append(row)
        
        if return_value == []:
            abort(406, message=f"Failed to find entry by {key} {value}")
        else: return return_value

    def pop_entry(self, id):

        data = self.csv_to_list()

        for row in data:
            if row['id'] == str(id):
                entry = row
                data.remove(row)
                break
        else: abort(406, message=f"Failed to find entry by id {id}")

        self.list_to_csv(data)
        return entry

    def add_entry(self, model, args):
        data = self.csv_to_list()
        id = int(data[-1]['id']) + 1
        new_entry = {'id': id, 'model': model}
        for key, value in args.items():
            if value is not None:
                new_entry[key] = value

        data.append(new_entry)
        self.list_to_csv(data)
        return f"Added data {new_entry}"

    def update_entry(self, args):
        data = self.csv_to_list()
        entry = self.find_entry('id', args['id'])[0]

        for row in data:
            if row['id'] == str(args['id']):
                for key, value in args.items():
                    if value is not None:
                        row[key] = value
                entry = row
                break

        self.list_to_csv(data)
        return entry
    def count_items(self):
        data = self.csv_to_list()
        counted = {}
        for row in data:
            if row['location'] == "Stock":
                if not row['model'] in counted:
                    counted[row['model']] = 1
                else: 
                    counted[row['model']] += 1
        return counted
    
    def to_stock(self, id):
        data = self.csv_to_list()
        for row in data:
            if row['id'] == str(id):
                row['location'] = "Stock"
                row['last_user'] = row['user']
                row['user'] = ""
                row['lastupdate'] = os.popen('date /T').read().strip() + " " + os.popen('time /T').read().strip()
                entry = row
                break
        else: abort(406, message=f"Failed to find entry by id {id}")

        self.list_to_csv(data)
        return entry

    def from_stock(self, id, user):
        data = self.csv_to_list()
        for row in data:
            if row['id'] == str(id):
                row['location'] = "User"
                row['user'] = user
                row['lastupdate'] = os.popen('date /T').read().strip() + " " + os.popen('time /T').read().strip()
                entry = row
                break
        else: abort(406, message=f"Failed to find entry by id {id}")

        self.list_to_csv(data)
        return entry

    def home(self):
        html = render_template('home.html', rows=self.csv_to_list())
        return make_response(html, 200, {"Content-Type": "text/html"})

    def get(self, key=None, value=None):
        if key == "All": 
            html = render_template('index.html', rows=self.csv_to_list())
            return make_response(html, 200, {"Content-Type": "text/html"})
        elif key == "table": 
            return self.csv_to_list()
        elif key == "summary": #TODO: "Beautify counter"
            return self.count_items() 
            html = render_template('index.html', rows=self.count_items())
            return make_response(html, 200, {"Content-Type": "text/html"})               
        elif key == "download_inventory":
            return send_file(self.csv_file, as_attachment=True, download_name="inventory.csv")
        elif key == "download_log":
            return send_file(self.log_file, as_attachment=True, download_name="inventory.log")
        elif key is None and value is None:
            return self.home()
        elif key is not None and value is not None:
            html = render_template('index.html', rows=self.find_entry(key, value))
            return make_response(html, 200, {"Content-Type": "text/html"})            

        else: return abort(400, message="Bad request")



    def put(self): #DONE
        put_parser = reqparse.RequestParser(bundle_errors= True)
        put_parser.add_argument('id', required=True)        
        for column in self.csv_file_columns:
            if column != "id":
                put_parser.add_argument(column)  
        put_parser.add_argument('user')                     
        args = put_parser.parse_args(strict=True)
        api_user = args.pop('api_user')        
        updated_entry = self.update_entry(args)

        self.log_action(api_user, f"Updated entry: {updated_entry}")
        return f"Updated entry: {updated_entry}"
    
    def post(self): #DONE
        post_parser = reqparse.RequestParser(bundle_errors= True)
        post_parser.add_argument('model', required=True)
        post_parser.add_argument('api_user', required=True)        
        for column in self.csv_file_columns:
            if column != "id" and column != "model":
                post_parser.add_argument(column)

        args = post_parser.parse_args(strict=True)
        api_user = args.pop('api_user')


        new_entry = self.add_entry(args['model'], args)
        self.log_action(api_user, f"New entry: {new_entry}")       
        return f"New entry: {new_entry}" 
        
    def patch(self):
        patch_parser = reqparse.RequestParser(bundle_errors= True)
        patch_parser.add_argument('id', required=True) 
        patch_parser.add_argument('action', required=True)
        patch_parser.add_argument('api_user', required=True)        
        patch_parser.add_argument('user')                
        args = patch_parser.parse_args(strict=True)
        api_user = args.pop('api_user')

        
        if args['action'] == "from_stock":
            if args['user'] is None:
                abort(406, message=f"User must be provided when taking item from stock")
            entry = self.from_stock(args['id'],args['user']) #TODO: Finish this method
        elif args['action'] == "to_stock":
            entry = self.to_stock(args['id']) #TODO: Finish this method
        else: abort(406, message=f"Unknown type_of_action {args['action']}")       


        self.log_action(api_user, f"Updated entry: {entry}")        
        return f"Updated entry: {entry}"    
    
    def delete(self): #DONE
        put_parser = reqparse.RequestParser(bundle_errors= True)
        put_parser.add_argument('id', required=True)          
        args = put_parser.parse_args(strict=True)        

        deleted_entry = self.pop_entry(args['id'])
        self.log_action("api_user", f"Deleted entry: {deleted_entry}")
        return f"Deleted entry: {deleted_entry}"     

if __name__ == "__main__":
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(StudentList, "/","/<string:key>", "/<string:key>/<string:value>")
    app.run(host="0.0.0.0", port=80, debug=True)
