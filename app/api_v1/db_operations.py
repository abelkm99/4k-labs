from .. import mongo
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
from . import make_response, jsonify, id_generator, current_app
import itertools

from PIL import Image
import base64
import io
import os


Member = mongo.db.Member
Project = mongo.db.Project
Token = mongo.db.Token
Application = mongo.db.Application
Project = mongo.db.Project
Task = mongo.db.Task
SuperAdmin = mongo.db.SuperAdmin
Event = mongo.db.Event


'''
delete all the information [for debuging]
'''


def _delteAll():
    Member.delete_many({})
    Project.delete_many({})
    Token.delete_many({})
    Application.delete_many({})
    Project.delete_many({})
    Task.delete_many({})
    SuperAdmin.delete_many({})
    Event.delete_many({})
    return make_response(jsonify(msg="all deleted"))


'''
    delte all the generated Tokens
'''


def _deleteTokens():
    Token.delete_many({})


'''
    delete all the members
'''


def _deleteMembers():
    Member.delete_many({})


'''
generate store and delete token
'''


def _storeToken(token, division):
    to = Token.insert_one({'token': token, 'Division': division})
    if to.inserted_id:
        res = {'token': token, 'Division': division}
        return make_response(jsonify(res), 200)
    else:
        # return 500 if it is not generated
        return make_response(jsonify({}), 500)


'''
get the division based on information given by the token

'''


def _get_division(token):
    token = Token.find_one({'token': token})
    return token['Division']


def _listToken():
    tokens = Token.find({}).sort([("_id", -1)])
    tokens = [{'token': x['token'], 'Division':x['Division']} for x in tokens]
    res = make_response(jsonify({'tokens': tokens}), 200)
    return res


# response should is 500 if no token has been deleted
def _deleteToken(token):
    delete_token = Token.delete_one({'token': token})
    if delete_token.deleted_count > 0:
        res = make_response(
            jsonify({'message': 'token has beend delted'}), 200)
        return res
    else:
        return make_response(jsonify({}), 500)


'''
    ******************
    register new admin
    ******************
'''


def _register_admin(data):
    num = SuperAdmin.find({"username": data["username"]}).count()
    if(num > 0):
        return {
            "message": 'username already exit'
        }
    else:
        # generate user id for the admin
        user_id = id_generator(12)
        members = SuperAdmin.find({'user_id': user_id}).count()
        while members != 0:
            user_id = id_generator(12)
            members = SuperAdmin.find({'user_id': user_id}).count()
        
        data['user_id'] = user_id
        register_member = SuperAdmin.insert_one(data)

        if register_member.inserted_id:
            msg = {'message': 'succesfully registerd'}
            return make_response(jsonify(msg), 200)
        else:
            msg = {"message": "Error registering the user"}
            return make_response(jsonify(msg), 500)


'''
    ******************
    register new members and login
    ******************
'''


def _register_member(data):
    num = Member.find({"email": data["email"]}).count()
    if(num > 0):
        msg = {"message": 'email address already registered'}
        return make_response(jsonify(msg)),409
    else:
        token = Token.find_one({'token': data['token']})
        if token:
            user_id = id_generator(12)
            members = Member.find({'user_id': user_id}).count()
            while members != 0:
                user_id = id_generator(12)
                members = Member.find({'user_id': user_id}).count()

            data['user_id'] = user_id
            data['Division'] = _get_division(data['token'])
            register_member = Member.insert_one(data)

            if register_member.inserted_id:
                msg = {'message': 'succesfully registerd'}
                token = Token.delete_one({'token': data['token']})
                return make_response(jsonify(msg), 200)
            else:
                msg = {"message": "Error registering the user"}
                return make_response(jsonify(msg), 500)
        else:
            msg = {'message': "invalid token"}
            return make_response(jsonify(msg), 401)


def _list_members():
    members = Member.find({})
    subset = ['password', '_id', 'token']
    members = [{key: value for key, value in member.items()
                if key not in subset} for member in members]
    res = make_response(jsonify({'members': members}), 200)
    return res


def _member_information(user_id):
    info = Member.find_one({'user_id': user_id})
    if info:
        subset = ['password', 'token', '_id']
        info = [{key: value
                 for key, value in info.items() if key not in subset}]
        info = info[0]
        return make_response(jsonify(info), 200)
    else:
        msg = {'message': "user name doesn't exist"}
        return make_response(jsonify(msg), 404)


def _delete_member(user_id):
    d_member = Member.delete_one({'user_id': user_id})
    if d_member.deleted_count > 0:
        res = make_response(
            jsonify({'message': 'Member has beend deleted'}), 200)
        return res
    else:
        msg = {'message': "username doesn't exist"}
        return make_response(jsonify(msg), 404)


def _update_profile_picture(image_data, user_id):
    profile_path = current_app.config['PROFILE_PICTURES']
    thumbnail_path = current_app.config['THUMBNAILS']

    decoded = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(decoded))
    if image.mode != "RGB":
        image = image.convert("RGB")

    img = image.resize((500, 500))
    img.save(os.path.join(profile_path, user_id+'.png'))

    img = image.resize((150, 150))
    img.save(os.path.join(thumbnail_path, user_id+'.png'))

    return user_id+'.png'


def _update_admin_profile(data):
    admin = SuperAdmin.find_one({'user_id': data['user_id']})
    if admin:
        if data.get('password') != None:
            if check_password_hash(admin.get('password'), str(data.get('password'))):
                del data['password']
                if data.get('newpassword') != None:
                    data['password'] = generate_password_hash(
                        data['newpassword'])
                    del data['newpassword']
                # alway add role and superadmin as true
                data['superadmin'] = True
                data['Role'] = admin['Role']
                update_admin = SuperAdmin.update_one(
                    {'user_id': data['user_id']},
                    {"$set": data}
                )
                # delete the password since it will be back as a response
                del data['password']

                if update_admin.matched_count > 0:
                    msg = {"message": "admin Profile has been updated succesfuly"}
                    return make_response(jsonify({'message': msg, 'data': data}), 200)
                else:
                    msg = {"message": "username doesn't exist"}
                    return make_response(jsonify(msg), 500)
            else:
                msg = {'message': 'incorrect password'}
                return make_response(jsonify(msg), 401)
        else:
            msg = {'message', 'password field is empty'}
            return make_response(jsonify(msg), 400)
    else:
        msg = {'message': "user id doesn't exits"}
        return make_response(jsonify(msg), 404)


def _update_information(data, user_id):
    # get the user using the user id and update the information
    # check if passwork is always reqired  to do the update information
    member = Member.find_one({'user_id': user_id})
    if member:
        if data.get('image') != None:
            profile_path = _update_profile_picture(data['image'], user_id)
            data['profile_picture'] = profile_path
            del data['image']
        data['Division'] = member['Division']
        data['user_id'] = user_id
        update_member = Member.update_one(
            {'user_id': user_id},
            {"$set": data}
        )
        data = Member.find_one({'user_id': user_id})
        del data['_id']
        if update_member.matched_count > 0:
            msg = {"message": "information has been updated succesfuly"}
            return make_response(jsonify({'message': msg, 'data': data}), 200)
        else:
            msg = {"message": "username doesn't exist"}
            return make_response(jsonify(msg), 500)
    else:
        msg = {'message': "user id doesn't exits"}
        return make_response(jsonify(msg), 404)


mapper = {
    0: 'intern',
    1: 'Regular member',
    2: 'Team Leader',
    3: 'Alumni',
    4: 'Admin'
}


def _change_role(data):
    #  change the string role in to an integer
    if not data['Role'].isnumeric():
        msg = {"message": "invalid role"}
        return make_response(jsonify(msg), 400)
    data['Role'] = int(data['Role'])
    # check if the given role exists inside the database

    if data['Role'] not in range(0, 5):
        msg = {"message": "invalid Role"}
        return make_response(jsonify(msg), 400)

    member = Member.find_one({"user_id": data['user_id']})

    if not member:
        msg = {"message": "invalid user_id"}
        return make_response(jsonify(msg), 404)

    if data['Role'] == 2:
        update_member = Member.update_one(
            {
                'Role': 2,
                'Division': member['Division']
            },
            {"$set": {'Role': 1}}
        )
        update_member = Member.update_one(
            {'user_id': data['user_id']},
            {"$set": {'Role': 2}}
        )
        if update_member.matched_count > 0:
            msg = {'message': "Role has been changed succesfully"}
            return make_response(jsonify(msg), 200)
        else:
            msg = {"message": "unkown error occured please try agai"}
            return make_response(jsonify(msg), 500)
    else:
        update_member = Member.update_one(
            {'user_id': data['user_id']},
            {"$set": {'Role': data['Role']}}
        )

        if update_member.matched_count > 0:
            msg = {'message': "Role has been changed succesfully"}
            return make_response(jsonify(msg), 200)
        else:
            msg = {"message": "unkown error occured please try again"}
            return make_response(jsonify(msg), 500)


'''
    update division take input of user_id,division from data
    changes the member in to regula members
'''


def _change_division(data):

    update_member = Member.update_one(
        {
            'user_id': data['user_id'],
        },
        {"$set": {
            'Role': 1,
            'Division': data['division']
        }
        }
    )
    if update_member.matched_count > 0:
        msg = {'message': "Division has been changed succesfully"}
        return make_response(jsonify(msg), 200)
    else:
        msg = {"message": "invalid user ID"}
        return make_response(jsonify(msg), 500)


def _submit_application(data):
    inserted_application = Application.insert_one(data)
    if inserted_application.inserted_id:
        msg = {"message": "file has been saved succesfully"}
        return make_response(jsonify(msg), 200)
    else:
        msg = {"message": "unknow internal server error"}
        return make_response(jsonify(msg), 500)


def _get_applicants():
    applicants = Application.find({}).sort("_id", -1)
    applicants = [x for x in applicants]
    subset = ['_id']
    applicants = [{key: value for key, value in app.items() if key not in subset}
                  for app in applicants]
    return make_response(jsonify({'applicants': applicants}), 200)


def _add_suggestion(data):
    app = Application.find_one({'id': data['id']})
    if app == None:
        msg = {'message': "error applicant id cant be found"}
        return make_response(jsonify(msg), 404)
    #  retrive the username
    app = Application.update_one(
        {"id": data["id"]},
        {"$push": {'suggestion': {data['user_id']: data['suggestion']}}}
    )
    if app.matched_count > 0:
        msg = {"message": "suggestion has been added"}
        return make_response(jsonify(msg), 200)
    else:
        msg = {"message": "unknow error "}
        return make_response(jsonify(msg), 500)


def _delete_all_applicanats():
    Application.delete_many({})


'''
create Project
'''


def _delete_allProjects():
    Project.delete_many({})
    Task.delete_many({})


def random_generator(collection_name, searching_query, size=10):
    code = id_generator(size)
    num = collection_name.find_one({searching_query: code})

    while num:
        code = id_generator(size)
        num = collection_name.find_one({searching_query: code})
    return code


def _create_project(data):

    project_code = random_generator(Project, 'project_code', 10)

    division = Member.find_one({"user_id": data["user_id"]})["Division"]

    project = {
        "project_code": project_code,
        "project_title": data["project_title"],
        "Division": division,
        "team_members": data["members"],
        "progress": 0,
        'github': data['github_link'],
        'docs': data['docs_link'],
        'description': data['description'],
        'deadline':data['deadline'],
        "project_leader":data['project_leader']
    }

    inserted_project = Project.insert_one(project)
    del project['_id']
    if not inserted_project:
        msg = {"message": "error creating the project"}
        return make_response(jsonify(msg), 500)
    tasks = []
    task_scheme = {
        "task": "",
        "project_code": project_code,
        "completed": 0
    }
    project['tasks'] = []
    for t in data["tasks"]:
        task_scheme['task'] = t
        task_scheme['task_code'] = random_generator(Task, 'task_code')
        project['tasks'].append(task_scheme.copy())
        tasks.append(task_scheme.copy())
    # only addes if there are tasks given by the user
    if len(tasks):
        Task.insert_many(tasks)

    members_information = []
    for user_id in project['team_members']:
        members_information.append(_get_teammember_information(user_id))
    project['members'] = project['team_members']
    project['team_members'] = members_information

    # add tasks to the project and return it as a response
    msg = {"message": "Project has been added successfully", 'project': project}
    return make_response(jsonify(msg), 200)


'''
info['value'] is used for profile picture component at the fron end
'''


def _get_teammember_information(user_id):
    info = Member.find_one({'user_id': user_id})
    if info:
        subset = ['Division', 'Full Name',
                  'profile_picture', 'user_id', 'username']
        info = [{key: str(value)
                 for key, value in info.items() if key in subset}]
        info = info[0]
        info['value'] = info['user_id']
        return info


def _get_all_projects():

    projects = Project.find({})
    subset = ['_id']
    data = []
    for project in projects:
        _calc_persentage(project['project_code'])
        pro = {}
        for k, v in project.items():
            if k not in subset:
                pro[k] = v

        tasks = Task.find({"project_code": pro.get('project_code')})
        tasks = [{k: v for k, v in task.items() if k not in subset}
                 for task in tasks]
        pro['tasks'] = tasks
        members_information = []
        for user_id in pro['team_members']:
            members_information.append(_get_teammember_information(user_id))
        pro['members'] = pro['team_members']
        pro['team_members'] = members_information
        data.append(pro)

    return make_response(jsonify({"projects": data}), 200)

def _get_all_info_portal(user_id,super_admin):
    
    projects = Project.find({})
    subset = ['_id']
    data = []
    for project in projects:
        _calc_persentage(project['project_code'])
        pro = {}
        for k, v in project.items():
            if k not in subset:
                pro[k] = v

        tasks = Task.find({"project_code": pro.get('project_code')})
        tasks = [{k: v for k, v in task.items() if k not in subset}
                 for task in tasks]
        pro['tasks'] = tasks
        members_information = []
        for user_code in pro['team_members']:
            members_information.append(_get_teammember_information(user_code))
        pro['members'] = pro['team_members']
        pro['team_members'] = members_information
        data.append(pro)

    members = Member.find({})
    subset = ['password', '_id', 'token']
    members = [{key: str(value) for key, value in member.items() if key not in subset} for member in members]

    subset = ['_id']
    events = Event.find({}).sort([("_id", -1)])
    events = [{k: v for k, v in event.items() if k not in subset}
              for event in events]
    tokens = Token.find({}).sort([("_id", -1)])
    tokens = [{'token': x['token'], 'Division':x['Division']} for x in tokens]

    info = ""
    if not super_admin:
        info = Member.find_one({'user_id': user_id})
        if info:
            subset = ['password', 'token', '_id']
            info = [{key: value
                    for key, value in info.items() if key not in subset}]
            info = info[0]
    if super_admin:
        info = SuperAdmin.find_one({'user_id': user_id})
        if info:
            subset = ['password', 'token', '_id']
            info = [{key: value
                    for key, value in info.items() if key not in subset}]
            info = info[0]

    return make_response(jsonify({"projects": data,"members":members,"events":events,"tokens":tokens,"user":info}), 200)



def _get_all_info():
    projects = Project.find({})
    subset = ['_id']
    data = []
    for project in projects:
        pro = {}
        for k, v in project.items():
            if k not in subset:
                pro[k] = v

        members_information = []
        for user_id in pro['team_members']:
            members_information.append(_get_teammember_information(user_id))
        pro['members'] = pro['team_members']
        pro['team_members'] = members_information 
        data.append(pro)

    members = Member.find({})
    subset = ['password', '_id', 'token']
    members = [{key: str(value) for key, value in member.items() if key not in subset} for member in members]

    subset = ['_id']
    events = Event.find({}).sort([("_id", -1)])
    events = [{k: v for k, v in event.items() if k not in subset}
              for event in events]
    return make_response(jsonify({"projects": data,"members":members,"events":events}), 200)


def _get_project(project_code):
    subset = ['_id']
    project = Project.find_one({'project_code': project_code})

    if not project:
        msg = {"message": "invalid project code"}
        return make_response(jsonify(msg), 404)

    project['_id'] = str(project.get('_id'))

    tasks = Task.find({"project_code": project_code})
    tasks = [{k: str(v) for k, v in task.items() if k not in subset}
             for task in tasks]
    project['tasks'] = tasks

    members_information = []
    for user_id in project['team_members']:
        members_information.append(_get_teammember_information(user_id))
    project['members'] = project['team_members']
    project['team_members'] = members_information

    return make_response(jsonify({"project": project}), 200)


'''
update project members
makes sure all the members that are assigned to the task are on the new update
'''


def _update_project_members(data):
    tasks = Task.find({'project_code': data['project_code']})
    all_members = [[member for member in task['assigned_to']]
                   for task in tasks]
    all_members = sum(all_members, [])
    for member in all_members:
        if member not in data['team_members']:
            msg = {'message': "can't remove members that are already assigned to tasks"}
            return make_response(jsonify(msg), 400)
    project = Project.update_one(
        {'project_code': data['project_code']},
        {
            "$set": {
                "team_members": data['team_members'],
            }
        }
    )

    if project.matched_count == 0:
        msg = {"message": "invalid project code"}
        return make_response(jsonify(msg), 400)
    msg = {"message": "project members has been updated successfully"}
    return make_response(jsonify(msg), 200)


def _delete_project(project_code):
    project = Project.find_one({'project_code': project_code})
    if not project:
        msg = {"message": "invalid project code"}
        return make_response(jsonify(msg), 404)

    project = Project.delete_one({'project_code': project_code})
    task = Task.delete_many({'project_code': project_code})
    return "Project has been succesfully delted", 200


'''
update project
'''


def _update_project(data):
    subset = ['project_title', 'github', 'docs', 'description', 'project_code','deadline','project_leader']
    project = Project.find_one(
        {'project_code': data.get('project_code', None)})
    if not project:
        msg = {"message": 'invalid project code'}
        return make_response(jsonify(msg)), 404
    new_data = {}
    for key in subset:
        new_data[key] = data.get(key, None) or project.get(key, None)
    team_members = project['team_members']
    if(data['project_leader'] not in team_members):
        team_members.append(data['project_leader'])
    update_project = Project.update_one(
        {"project_code": data['project_code']},
        {
            "$set": {
                "project_title": data['project_title'],
                "github": data['github'],
                "docs": data['docs'],
                "description": data['description'],
                "deadline":data["deadline"],
                "project_leader":data["project_leader"],
                "team_members":team_members
            }
        }
    )
    if update_project.matched_count > 0:
        msg = {"message": "Project has been updated succesfully"}
        return make_response(jsonify(msg), 200)
    else:
        msg = {"message": 'invalid project code'}
        return make_response(jsonify(msg)), 404
    pass


'''
    when task is completed 
    updare the progress
'''


def _calc_persentage(project_code):
    num_completed = Task.find(
        {'project_code': project_code, 'status': 2}).count()
    total = Task.find({'project_code': project_code}).count()

    #  to make sure it doesn't devode itself by zero
    if total:
        progress = num_completed/total * 100
    else:
        progress = 0

    progress = round(progress, 2)
    update_project = Project.update_one(
        {"project_code": project_code},
        {
            "$set": {
                "progress": progress,
            }
        }
    )

    pass


def _UpdateTaskStatus(task_code, status):

    task = Task.find_one({"task_code": task_code})
    if not task:
        msg = {"message": "invalid task code was provided"}
        return make_response(jsonify(msg), 404)

    updated_task = Task.update_one(
        {"task_code": task_code},
        {
            "$set": {
                "status": int(status),
            }
        }
    )

    _calc_persentage(task['project_code'])

    msg = {"message": "task is updated succesfully"}
    return make_response(jsonify(msg), 200)


def _assignTaskMembers(data):
    u_task = Task.update_one(
        {"task_code": data['task_code']},
        {
            "$set": {"assigned_to": data['members']}
        }
    )
    if u_task.matched_count > 0:
        msg = {"message": " assigned members for the task has been updated  succesfully"}
        return make_response(jsonify(msg), 200)

    msg = {"message": "invalid task code"}
    return make_response(jsonify(msg), 400)


def _addTask(data):
    project = Project.find_one({'project_code': data['project_code']})
    if not project:
        msg = {"messge": "project doesn't exist"}
        return make_response(jsonify(msg), 404)
    task = {
        "task": data['task'],
        "project_code": data['project_code'],
        "completed": 0,
        "status": 0,
        "assigned_to": []
    }
    task['task_code'] = random_generator(Task, 'task_code')
    t_copy = task.copy()
    Task.insert_one(task)
    msg = {'message': 'task has been added succesully', 'task': t_copy}
    return make_response(jsonify(msg), 200)


def _deleteTask(task_code):
    d_task = Task.delete_one({'task_code': task_code})
    if d_task.deleted_count == 0:

        msg = {"message": "no task has been deleted"}
        return make_response(jsonify(msg), 400)
    msg = {"message": "task has been successfully added"}
    return make_response(jsonify(msg), 200)


def _rename_task(data):
    u_task = Task.update_one(
        {"task_code": data['task_code']},
        {
            "$set": {"task": data['task']}
        }
    )
    if u_task.matched_count > 0:
        msg = {"message": "task has been renamed succesfully"}
        return make_response(jsonify(msg), 200)

    msg = {"message": "invalid task code"}
    return make_response(jsonify(msg), 400)


def _rename_project(data):
    u_project = Project.update_one(
        {"project_code": data['project_code']},
        {
            "$set": {"project_title": data['project_title']}
        }
    )
    if u_project.matched_count > 0:
        msg = {"message": "project has been renamed succesfully"}
        return make_response(jsonify(msg), 200)

    msg = {"message": "invalid project code"}
    return make_response(jsonify(msg), 400)


'''
login checker for admin
'''


def _check_username_password_admin(email):
    s_admin = SuperAdmin.find_one({'username': email})
    passed = False
    subset = ['password', '_id']
    if s_admin:
        s_admin = _remover(subset, s_admin)
        passed = True
        return s_admin, passed
    else:
        msg = {"message": "this email address is not registerd"}
        return msg,passed


'''
login checker
'''


def _check_username_password(email):
    member = Member.find_one({'email': email})
    subset = ['password', '_id']
    passed = False
    if member:
        member = _remover(subset, member)
        passed = True
        return member, passed
    else:
        msg = {"message": "username doesn't exist"}
        return msg,passed


'''
return a dictionary exsplicit of given array

'''


def _remover(arr, dict):
    data = {}
    for key, value in dict.items():
        if key not in arr:
            data[key] = value
    return data


'''
    add new event 
'''


def _add_event(data):
    data['event_id'] = random_generator(Event, 'event_id', 10)
    data['event_image'] = _save_event(data['event_image'], data['event_id'])
    event = Event.insert_one(data)
    del data['_id']
    if event.inserted_id:
        res = {'message': 'event has been created', 'event': data}
        return make_response(jsonify(res), 200)
    else:
        return make_response(jsonify({'message': 'error while creating the event'}), 400)


'''
    get all the events 
'''


def _get_events():
    subset = ['_id']
    events = Event.find({}).sort([("_id", -1)])
    events = [{k: v for k, v in event.items() if k not in subset}
              for event in events]
    return make_response(jsonify(events=events), 200)


'''
    save event images
'''


def _save_event(image_data, event_id):
    event_path = current_app.config['EVENTS']

    if not os.path.exists(event_path):
        os.mkdir(event_path)

    decoded = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(decoded))
    if image.mode != "RGB":
        image = image.convert("RGB")

    img = image.resize((1280, 720))
    img.save(os.path.join(event_path, event_id+'.png'))

    return event_id+'.png'


'''
    delete event image after image is delted
'''


def _delte_event_image(images):
    event_path = current_app.config['EVENTS']

    for image in images:
        path = os.path.join(os.getcwd(), event_path, image)
        os.remove(path)


def _delete_event(event_id):
    event = Event.find_one({'event_id': event_id})
    event_images = event['event_gallery']
    event_images.append(event['event_image'])
    _delte_event_image(event_images)
    delete_event = Event.delete_one({'event_id': event_id})
    if delete_event.deleted_count:
        msg = {"message": "event has been deleted successfully"}
        return make_response(jsonify(msg), 200)
    else:
        msg = {"message": "event id doesn't exist"}
        return make_response(jsonify(msg), 404)
