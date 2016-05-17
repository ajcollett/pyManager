# This code is free to use! It comes with no Warrenties however.
# If you want to help make it better, please let me know about
# any changes.

# This is intended to help you pull your JSON objects from manager.
import requests
import argparse
import getpass
from BeautifulSoup import BeautifulSoup

__author__ = 'Andrew James Collett'


class manager_objects:

    def __init__(self, host, user, business):
        self.host = host
        self.user = user
        self.session = requests.Session()
        self.session.auth(user, getpass.getpass())
        self.business = self.get_business(business)
        self.index = self.get_index_of_collections()

    # This is the base method to get the url
    def get_encodedURL(self, requestURL):
        r = self.session.get('https://' + self.host + requestURL)
        return r

    # Get the business
    def get_business(self, business):
        json_index = self.get_encodedURL('/api/index.json').json()
        for pair in json_index:
            if pair['Name'] == business:
                return pair['Key']
        return None

    # Get the index for the business collections
    def get_index_of_collections(self):
        index = dict()
        r = self.get_encodedURL('/api/' + self.business)
        soup = BeautifulSoup(r.text)
        for link in soup.findAll('a'):
            index[link.getText()] = link.get('href')

        return index

    # Get the index for the collection
    def get_index_of_objects(self, collection_path):
        return self.get_encodedURL(collection_path + '/index.json').json()

    def get_objects_from_index(self, object_index):
        objects = dict()
        for object in object_index:
            objects[object] = self.get_encodedURL('/api/' + self.business +
                                                  '/' + object + '.json'
                                                  ).json()
        return objects


# Create the arguments parser
def define_args():
    parser = argparse.ArgumentParser(description='API calls for manager')
    parser.add_argument('host')
    parser.add_argument('user')
    parser.add_argument('business')
    parser.add_argument('object')
    return parser


# Do the main thing
def __main__():

    parser = define_args()
    args = parser.parse_args()

    gom = manager_objects(args.host, args.user, args.business)
    object_index = gom.get_index_of_objects(gom.index[args.object])
    print object_index
    print gom.get_objects_from_index(object_index)

if __name__ == '__main__':
    __main__()
