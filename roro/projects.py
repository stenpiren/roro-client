import os
import shutil
import yaml
import firefly
from . import models

SERVER_URL = "https://api.rorocloud.io/"

def login(email, password):
    client = firefly.Client(SERVER_URL)
    return client.login(email=email, password=password)

class Project:
    def __init__(self, name, runtime=None):
        self.name = name
        self.runtime = runtime
        self.client = firefly.Client(SERVER_URL)

    def create(self):
        return self.client.create(name=self.name)

    def run(self, command):
        job = self.client.run(project=self.name, command=command)
        return job

    def run_notebook(self):
        job = self.client.run_notebook(project=self.name)
        return job

    def ps(self, jobid=None):
        return self.client.ps(project=self.name, jobid=jobid)

    def logs(self, jobid):
        return self.client.logs(project=self.name, jobid=jobid)
        #return self.client.logs(project=self.name)

    def deploy(self):
        archive = self.archive()
        size = os.path.getsize(archive)
        with open(archive, 'rb') as f:
            format = 'tar'
            response =  self.client.deploy(
                project=self.name,
                archived_project=f,
                size=size,
                format=format
            )
        return response

    def archive(self, format='tar'):
        root_dir = os.path.realpath(os.path.curdir)
        dir_name = os.path.basename(root_dir)
        return shutil.make_archive(dir_name, format)

    def get_config(self):
        return self.client.get_config(project=self.name)

    def set_config(self, config_vars):
        return self.client.set_config(project=self.name, config_vars=config_vars)

    def unset_config(self, names):
        return self.client.unset_config(project=self.name, names=names)

    def list_volumes(self):
        volumes = self.client.volumes(project=self.name)
        return [volume['volume'] for volume in volumes]

    def add_volume(self, volume_name):
        volume =  self.client.add_volume(project=self.name, name=volume_name)
        return volume['volume']

    def get_model_repository(self, name):
        """Returns the ModelRepository from this project with given name.
        """
        return models.get_model_repository(project=self.name, name=name)

    @staticmethod
    def find_all():
        client = firefly.Client(SERVER_URL)
        projects = client.projects()
        return [Project(p['name'], p.get('runtime')) for p in projects]

def current_project():
    if os.path.exists("roro.yml"):
        d = yaml.safe_load(open("roro.yml"))
        return Project(d['project'], d.get('runtime', 'python36'))
    else:
        raise Exception("Unable to find roro.yml")

get_current_project = current_project

def list_projects():
    return Project.find_all()
