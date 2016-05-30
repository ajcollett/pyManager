# This code is free to use! However, it comes with no warrenties.
# Please let me know about any improvements
# Repo at https://github.com/ajcollett/pyManager

"""API calling script for Manager.io."""
import requests
import argparse
import getpass
from threading import Thread
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
        self.index = self.index_collections()

    def get_encodedURL(self, requestURL):
        """Fetch the URL."""
        r = self.session.get(self.root_url + requestURL)
        return r

    def post_encodedURL(self, data, collection_path):
        """Post to the URL."""
        r = self.session.post(self.root_url + collection_path, data=data)
        return r

    def get_business(self, business):
        """Fetch the path to the specific business."""
        json_index = self.get_encodedURL('/api/index.json').json()
        for pair in json_index:
            if pair['Name'] == business:
                return pair['Key']
        return None

    def index_collections(self):
        """Fetch the paths to the collection."""
        index = dict()
        r = self.get_encodedURL('/api/' + self.business)
        soup = BeautifulSoup(r.text)
        for link in soup.findAll('a'):
            index[link.getText()] = link.get('href')

        return index

    def index_objects(self, collection_path):
        """Fetch all the paths to the objects."""
        return self.get_encodedURL(collection_path + '/index.json').json()

    def get_object_thread(self, o_dict, index):
        o_dict[index] = self.get_encodedURL('/api/' + self.business +
                                            '/' + index + '.json'
                                            ).json()

    def get_objects(self, object_index):
        """
        Fetch each object from manager.

        This function is a little hacky at the moment, it needs threads to
        perform at any decent speed.
        """
        objects = dict()
        threads = dict()
        cnt = 0

        for object in object_index:
            threads[object] = Thread(target=self.get_object_thread,
                                     args=(objects, object))
            cnt = cnt + 1
            threads[object].start()
            """
            objects[object] = self.get_encodedURL('/api/' + self.business +
                                                   '/' + object + '.json'
                                                   ).json()
                                                """
            if cnt == 150:
                for thread in threads:
                    threads[thread].join()
                cnt = 0
                threads = dict()

        for thread in threads:
            threads[thread].join()
        # for object in object_index:
            # threads[object].join()

        return objects

    def put_object(self, data, object_path):
        """Put an object at that specific path."""
        print('Not yet implemented')
        pass

    def post_object(self, data, collection_path):
        """Post an object at that specific path."""
        r = self.post_encodedURL(data, collection_path)

        if '201' not in r.status_code:
            print('Something went wrong', r.status_code)
            print collection_path
            print data

        return r

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
    object_index = gom.index_objects(gom.index[args.object])
    print(object_index)
    print(gom.get_objects(object_index))

if __name__ == '__main__':
    __main__()
