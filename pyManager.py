# This code is free to use! However, it comes with no warrenties.
# Please let me know about any improvements
# Repo at https://github.com/ajcollett/pyManager

"""API calling script for Manager.io."""
import requests
import argparse
import getpass
from BeautifulSoup import BeautifulSoup

__author__ = 'Andrew James Collett'
__title__ = 'pyManager'
__email__ = 'andrewjamescollett@gmail.com'
__license__ = 'LGPL3'
__copyright__ = 'Copyright 2016 Andrew James Collett'


class manager_object:
    """Represents the info from the the manager.io."""

    def __init__(self, root_url, user, business):
        """Create the Manager object.

        Start the session, get the businss and the index of collections
        """
        self.root_url = root_url
        self.user = user
        self.session = requests.Session()
        self.session.auth = (user, getpass.getpass())
        self.business = self.get_business(business)
        self.index = self.get_index_of_collections()

    def get_encodedURL(self, requestURL):
        """Fetch the URL."""
        r = self.session.get(self.root_url + requestURL)
        return r

    def get_business(self, business):
        """Fetch the path to the specific business."""
        json_index = self.get_encodedURL('/api/index.json').json()
        for pair in json_index:
            if pair['Name'] == business:
                return pair['Key']
        return None

    def get_index_of_collections(self):
        """Fetch the paths to the collection."""
        index = dict()
        r = self.get_encodedURL('/api/' + self.business)
        soup = BeautifulSoup(r.text)
        for link in soup.findAll('a'):
            index[link.getText()] = link.get('href')

        return index

    def get_index_of_objects(self, collection_path):
        """Fetch all the paths to the objects."""
        return self.get_encodedURL(collection_path + '/index.json').json()

    def get_objects_from_index(self, object_index):
        """Fetch each object from manager."""
        objects = dict()
        for object in object_index:
            objects[object] = self.get_encodedURL('/api/' + self.business +
                                                  '/' + object + '.json'
                                                  ).json()
        return objects

    def put_object(self, data, object_path):
        """Put an object at that specific path."""
        print('Not yet implemented')
        pass

    def post_object(self, data, object_path):
        """Post an object at that specific path."""
        print('Not yet implemented')
        pass

    def del_object(self, object):
        """Delete the specified object."""
        print('Not yet implemented')
        pass


def define_args():
    """We define the arguents here for the command line."""
    parser = argparse.ArgumentParser(description='API calls for manager')
    parser.add_argument('root_url')
    parser.add_argument('user')
    parser.add_argument('business')
    parser.add_argument('object')
    return parser


def __main__():
    """For the CLI, at the moment a test runner."""
    parser = define_args()
    args = parser.parse_args()

    gom = manager_object(args.root_url, args.user, args.business)
    object_index = gom.get_index_of_objects(gom.index[args.object])
    print(object_index)
    print(gom.get_objects_from_index(object_index))

if __name__ == '__main__':
    __main__()
