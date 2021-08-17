from . import api_v1,current_app
from . import db_operations,id_generator
from flask import request,jsonify,send_from_directory,make_response,send_file
import secrets
from werkzeug.utils import secure_filename
import os
import time
from . import *
from functools import wraps
from .. import auth



roleMap = {
    'intern':0,
    'regular_member':1,
    'team_leader':2,
    'alumni':3,
    'admin':4,
}


'''
create decorators for intern,regular_member,team_leader,alumni,admin,super_admin
'''

def role_required(roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["Role"] in roles:
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="user doesn't have permission to access the files!"), 403

        return decorator

    return wrapper


'''
create decoretors to store user infromation
'''

'''
this are used for debuging will be removed during production
'''
# @api_v1.after_request
# def after_request(response):
#     print(request.referrer)
#     response.headers.add("Access-Control-Allow-Origin", request.referrer);
#     response.headers.add("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS,POST,PUT");
#     response.headers.add("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept, Authorization");
#     return response


@api_v1.route('/api_v1/delete_all_tokens')
def delete_all_tokens():
    db_operations._deleteTokens()
    return "succesully deleted all tokens"

@api_v1.route('/api_v1/delete_all_memebers')
def delete_all_memebers():
    db_operations._deleteMembers()
    return "succesully deleted all Members"

@api_v1.route('/api_v1/deleteall')
def deleteall():
   return db_operations._delteAll()

'''
    TokeGenerator
    generate Token with Division
'''


@api_v1.route('/api_v1/generate_token',methods=['POST'])
@role_required([roleMap.get('admin')])
def generate_token():
    req = request.get_json()
    token = secrets.token_urlsafe()
    res = db_operations._storeToken(str(token),str(req['Division']))
    return res

#  list all the generated tokens
@api_v1.route('/api_v1/list_tokens')
@role_required([roleMap.get('admin')])
def list_tokens():
    return db_operations._listToken()
    
@api_v1.route('/api_v1/delete_token/<token>')
@role_required([roleMap.get('admin')])
def delete_token(token):
    return db_operations._deleteToken(str(token))


'''
Register an Admin

this line will be deleted
'''

# @api_v1.route('/api_v1/register_admin',methods=['POST'])
# def register_admin():
#     req = request.get_json()
#     if not req:
#         msg = {"message":"invalid input"}
#         return jsonify(msg),400
#     if req.get('email',None)==None:
#         msg = {"message":"all information is not provided"}
#         return jsonify(msg),400
#     data = {
#         'profile_picture':'',
#         'Discription':'',
#         'Linkden':'',
#         'Github':'',
#         'Role':4,
#         'Division':'',
#         'projects':None,
#         'username':req.get('email'),
#         'superadmin':True,
#     }
#     return db_operations._register_admin(data)

'''
    To register only username,password Full Name and Token are needed
'''


@api_v1.route('/api_v1/register_member',methods=['POST'])
def register_member():
    req = request.get_json()

    if not req:
        msg = {"message":"invalid input"}
        return jsonify(msg),400
    if not (req.get('email',None) and req.get('token',None) and req.get('username',None)):
        msg = {"message":"all information is not provided"}
        return jsonify(msg),400
    data = {
        'profile_picture':'',
        'Discription':'',
        'Linkden':'',
        'Github':'',
        'Role':0,
        'Division':'',
        'projects':None,
        'username':req.get('username'),
        'email':req.get('email'),
        'fullname':req.get('fullname'),
        'token':req.get('token'),
        'superadmin': False
    }
    return db_operations._register_member(data)


@api_v1.route('/api_v1/members')
def list_memebers():
    return db_operations._list_members()

@api_v1.route('/api_v1/members/<user_id>')
def member(user_id):
    return db_operations._member_information(str(user_id))

'''
Delete a memeber 
        req = {
                "user_id":"BWQ8GQ9CGCOA"
              }
            
'''
@api_v1.route('/api_v1/delete_member',methods=['POST'])
@role_required([roleMap.get('admin')])
def delete_member():
    req = request.get_json()
    return db_operations._delete_member(str(req['user_id']))


'''
Admin login
'''

@api_v1.route('/api_v1/adminlogin',methods=['POST'])
def adminlogin():
    req = request.get_json()
    if not req:
        msg = {"message":"invalid input"}
        return jsonify(msg),400
    if req.get('id_token',None) == None:
        msg = {"message":"invalid input"}
        return jsonify(msg),400
    try:
        idinfo = auth.verify_id_token(req.get("id_token"))
    except ValueError:
        return jsonify({"message":"Could not verify audience."}),400
    data,authenticated = db_operations._check_username_password_admin(idinfo['email'])
    if authenticated:
        data['profile_picture'] = idinfo['picture']
        additional_claims = data
        access_token = create_access_token(identity=data['user_id'],additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=data['user_id'])
        return jsonify(access_token=access_token,user= data,refresh_token=refresh_token),200
    else:
        return jsonify(data),404


'''
do LOGIN here
'''

@api_v1.route('/api_v1/login',methods=['POST'])
def login():
    req = request.get_json()
    if not req:
        msg = {"message":"invalid input"}
        return jsonify(msg),400
    if req.get('id_token',None) == None:
        msg = {"message":"invalid input"}
        return jsonify(msg),400
    try:
        idinfo = auth.verify_id_token(req.get("id_token"))
    except ValueError:
        return jsonify({"message":"Could not verify audience or invalid token."}),400
    data,authenticated = db_operations._check_username_password(idinfo['email'])
    if authenticated:
        additional_claims = data
        access_token = create_access_token(identity=data['user_id'],additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=data['user_id'])
        return jsonify(access_token=access_token,user= data,refresh_token=refresh_token),200
    else:
        return jsonify(data),404
'''
    TODO:
        [] make sure first if the user is logged in before updating any information
        [x] username must be sent or loaded from the information
        [] make sure the user name is taken form session 

'''
@api_v1.route('/api_v1/<user_id>/upadate_infromation',methods=['PUT'])
@jwt_required(locations=["headers"])
def update_information(user_id):
    req = request.get_json(force=True)
    subset = ['Linkden','Github','fullname','Discription','image','username']
    data = {}
    for key,value in req.items():
        if key in subset and len(value):
            data[key] = value
    return db_operations._update_information(data,str(user_id))

'''
update Admin profile
'''

@api_v1.route('/api_v1/upadate_admin_profile',methods=['PUT'])
@jwt_required(locations=["headers"])
def upadate_admin_profile():
    req = request.get_json(force=True)
    if req==None:
        msg = {'message':'invalid request'}
        return jsonify(msg),400
    return db_operations._update_admin_profile(req)

'''
  req =   {
            "user_id":"{user id of the memember}",
            "Role":"2"
        }

'''

@api_v1.route('/api_v1/changeRole',methods=['PUT'])
@role_required([roleMap.get('admin')])
def changeRole():
    req = request.get_json()
    return db_operations._change_role(req)


@api_v1.route('/api_v1/changeDivision',methods=['POST'])
@jwt_required(locations=["headers"])
def changeDivision():
    divisions = ["DEVS",'BOTS','THINGS']
    req = request.get_json()
    if not req:
        msg = {'message':'invalid request'}
        return jsonify(msg),400
    if req.get('user_id',None)==None or req.get('division',None)==None:
        msg = {'message':'invalid request'}
        return jsonify(msg),400
    if req.get('division') not in divisions:
        msg = {'message':'invalid Division'}
        return jsonify(msg),400
    return db_operations._change_division(req)


@api_v1.route('/api_v1/sendApplication',methods=['POST'])
def sendApplication():
    data = request.form.to_dict()
    data ['suggestion'] = []
    # make sure if the path is created
    if not (os.path.exists(current_app.config['CV_PATH'])):
        os.mkdir(current_app.config['CV_PATH'])
    # check if the given name is acceptable
    file = request.files['file']
    extention = file.filename.split('.')[-1]
    generated_id = id_generator(4)
    if extention in current_app.config['ALLOWED_EXTENSIONS']:
        filename = data['FUll Name'].split(' ')[0]+generated_id
        path = os.path.join(current_app.config['CV_PATH'],filename+'.'+extention)

        #  check if there is duplication before
        while path in os.listdir(current_app.config['CV_PATH']):
            generated_id = id_generator(3)
            filename = data['FUll Name'].split(' ')[0]+generated_id
            path = os.path.join(current_app.config['CV_PATH'],filename+'.'+extention)
        # add it to dictionary and download it

        # file.save(path)
        data['path'] = path
        data['id'] = generated_id
        return db_operations._submit_application(data)
    else:
        msg = {"message":"unknow internal server error"}
        return jsonify(msg),500

'''
    donwload the cv that has been uploaded
    TODO:
        [] the download is not working

'''

@api_v1.route('/api_v1/cv/<filename>')
@jwt_required(locations=["headers"])
def download_cv(filename):
    return send_from_directory(current_app.config['CV_PATH'],filename,as_attachment=True)


'''
    List all the applicants
    this will be displayed for the admin and teamleaders only
    TODO:
        [] deleting the applicant information is not that neccessay but must be done at the futre
        [] use the path as a uniqe key 
'''
@api_v1.route('/api_v1/see_applicants')
@role_required([roleMap.get('admin')])
def seeApplicants():
    return db_operations._get_applicants()

# suggest an applicant this is opetional the Team leader has an option to add this information or leave 
#  it as it is

@api_v1.route('/api_v1/add_suggestion',methods=['POST'])
@role_required([roleMap.get('team_leader')])
def add_suggestion():
    req = request.get_json()
    return  db_operations._add_suggestion(req)

'''
    delete all the applicants used for debuging
'''

@api_v1.route('/api_v1/delete_all_applicanats')
@role_required([roleMap.get('admin')])
def delete_all_applicanats():
    db_operations._delete_all_applicanats()
    return  "all the applications are delted succesfully"

'''
    Projects
        [] create Project
        [] member can submit subtask if they are only the member of the projec update Project
        [] read_Projects in detail and documentation
        [] view specific project
    schema

        project
            {
                '_id':'given by mobgodb',
                'project id':-> this is randomly generated and make sure there is no duplicate
                'project name':->given from the user,
                'subtasks':->
                'Division':->from the Team Leader who created the project
                'team members':->[array of user_id],
                'github'
                'google docks'
            }

        subtask 
        {
            '_id', given by the mongo
            'sub task': ->given from the user
            'project id',
            'finished':false
        }
'''

@api_v1.route('/api_v1/create_new_project',methods=['POST'])
def create_new_project():
    req = request.get_json()
    return db_operations._create_project(req)

@api_v1.route('/api_v1/get_projects')
def get_projects():
    return db_operations._get_all_projects()


'''
this route returns all the projects with out including the tasks for the portal
'''
@api_v1.route('/api_v1/get_all_info_portal')
def get_all_info_portal():
    verify_jwt_in_request()
    claims = get_jwt()
    return db_operations._get_all_info_portal(claims['user_id'],claims['superadmin'])

'''
this route returns all the projects with out including the tasks for the static pages
'''
@api_v1.route('/api_v1/_get_all_info')
def _get_all_info():
    return db_operations._get_all_info()


@api_v1.route('/api_v1/get_projects/<project_code>')
def get_project(project_code):
    return db_operations._get_project(project_code)

@api_v1.route('/api_v1/project/updatemembers',methods=['POST'])
@jwt_required()
def update_project_members():
    req = request.get_json()
    if req == None:
        return jsonify("invalid request"),400
    elif req.get('project_code',None) == None:
        return jsonify(msg="please provide a valid project code"),400
    if req.get('team_members',None) == None or len(req.get('team_members')) == 0:
        return jsonify(msg="no team member is provided please provide at least one member for the project"),400
    return db_operations._update_project_members(req)

'''
    on every update of project task
'''

'''
    delete project 
    also deltes all the subtasks of the project
'''
@api_v1.route('/api_v1/delete_project/<project_code>')
@role_required([roleMap.get('admin')])
def delete_project(project_code):
    return db_operations._delete_project(project_code)

'''
    update project tittle,github link,docks link,Description
'''

@api_v1.route('/api_v1/updateproject',methods=['POST'])
@role_required([roleMap.get(x) for x in roleMap])
def update_project():
    req = request.get_json()
    if not req:
        msg = {'message':'invalid input'}
        return jsonify(msg),400
    if not req.get('project_code',None):
        msg = {'message':'empty project code'}
        return jsonify(msg),400
    return db_operations._update_project(req)


@api_v1.route('/api_v1/updateTask', methods = ['PUT'])
@jwt_required(locations=["headers"])    
def updateTask():
    req = request.get_json()
    print(req)
    if not req:
        msg = {"message":"invalid request"}
        return jsonify(msg),400
    if req.get('task_code',None) == None or req.get('status',None) == None:
        msg = {"message":"all inputs are required"}
        return jsonify(msg),400
    return db_operations._UpdateTaskStatus(req['task_code'],req['status'])

@api_v1.route('/api_v1/addTask', methods = ['POST'])
@role_required([v for k,v in roleMap.items()])
def addTask():

    req = request.get_json()
    #  if it is none
    if not req:
        msg = {"message":"invalid input"}
        return jsonify(msg),400
    
    if not req.get('project_code') or len(req.get('task'))<1:
        msg = {"message":"invalid input"}
        return jsonify(msg),400
    return db_operations._addTask(req)

@api_v1.route('/api_v1/task/assign_member', methods = ['PUT'])
@role_required([v for k,v in roleMap.items()])
def assign_member():
    req = request.get_json()
    if not req:
        msg = {"message":"invalid input"}
        return jsonify(msg),400

    if  req.get('task_code',None) == None or req.get('members',None)==None:
        msg = {"message":"all input are required"}
        return jsonify(msg),400
    return db_operations._assignTaskMembers(req)

'''
delete a task 
'''

@api_v1.route('/api_v1/deleteTask/<task_code>', methods = ['POST'])
@jwt_required(locations=["headers"])
def deleteTask(task_code):
    return db_operations._deleteTask(task_code)

@api_v1.route('/api_v1/renameTask', methods = ['POST'])
@jwt_required(locations=["headers"])
def renameTask():
    req = request.get_json()
    #  if it is none
    if not req:
        msg = {"message":"invalid input"}
        return jsonify(msg),400
    if not req.get('task_code') or len(req.get('task'))<1:
        msg = {"message":"invalid input"}
        return jsonify(msg),400
    return db_operations._rename_task(req)

@api_v1.route('/api_v1/renameProject', methods = ['POST'])
@role_required([roleMap.get('team_leader')])
def renameProject():
    req = request.get_json()
    #  if it is none
    if not req:
        msg = {"message":"invalid input"}
        return jsonify(msg),400
    if not req.get('project_code') or len(req.get('project title'))<1:
        msg = {"message":"invalid input"}
        return jsonify(msg),400
    return db_operations._rename_project(req)

@api_v1.route('/api_v1/get_profile/<image>')
def get_image(image):
    profile_path = current_app.config['PROFILE_PICTURES']

    path = os.path.join(os.getcwd(),profile_path,image)

    if os.path.exists(path):
        return send_file(path, mimetype='image/jpg')
    return jsonify({'message':"file doesn't exist"}),404

@api_v1.route('/api_v1/get_thumbnail/<image>')
@jwt_required(locations=["headers"])
def get_thumbnail(image):
    thumbnail_path = current_app.config['THUMBNAILS']

    path = os.path.join(os.getcwd(),thumbnail_path,image)

    if os.path.exists(path):
        return send_file(path, mimetype='image/jpg')
    return jsonify({'message':"file doesn't exist"}),404


@api_v1.route('/api_v1/add_event', methods=['POST'])
@role_required([roleMap.get('admin')])
def add_event():
    req = request.get_json()
    if not req:
        return jsonify('invalid input'),400
    if not(req.get('event_title',None) and req.get('event_description',None) and req.get('event_start',None) and req.get('event_end',None) and req.get('event_image',None)):
        return jsonify('all input are necessary'),400
    return db_operations._add_event(req)

@api_v1.route('/api_v1/get_events', methods=['GET'])
@role_required([roleMap.get('admin')])
def get_events():
    return db_operations._get_events()

@api_v1.route('/api_v1/get_event/<image>')
def get_event_image(image):
    event_path = current_app.config['EVENTS']

    path = os.path.join(os.getcwd(),event_path,image)

    if os.path.exists(path):
        return send_file(path, mimetype='image/jpg')
    return jsonify({'message':"file doesn't exist"}),404


@api_v1.route('/api_v1/delete_event/<event_id>')
@role_required([roleMap.get('admin')])
def delete_event(event_id):
    return db_operations._delete_event(event_id)

@api_v1.route('/api_v1/get_event_gallery/<event_gallery_id>')
def get_event_gallery_images(event_gallery_id):
    events_path = current_app.config['EVENTS']

    path = os.path.join(os.getcwd(),events_path,event_gallery_id)

    if os.path.exists(path):
        return send_file(path, mimetype='image/jpg')
    return jsonify({'message':"file doesn't exist"}),404


@api_v1.route('/api_v1/update_event/<event_id>',methods=['POST'])
# @role_required([roleMap.get('admin')])
def update_event(event_id):
    req = request.get_json(force=True)
    subset = ['event_title','event_image','event_start','event_end','event_description','new_galley_images','tobe_deleted_images']
    update_data = {}
    for key,value in req.items():
        if key in subset and len(value):
            update_data[key] = value
    return db_operations._update_event(event_id,update_data)


