#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This code is free to use! However, it comes with no warrenties.
# Please let me know about any improvements
# Repo at https://github.com/ajcollett/pyManager
# Requires python 2.7.11 or up

"""API calling script for Manager.io."""
import requests
import argparse
import getpass
import json
from threading import Thread
from bs4 import BeautifulSoup
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
        self.collections = self.index_collections()

    def get(self, requestURL):
        """Fetch the URL."""
        return self.session.get(self.root_url + requestURL)

    def get_business(self, business):
        """Fetch the path to the specific business."""
        json_index = self.get('/api/index.json').json()
        for pair in json_index:
            if pair['Name'] == business:
                return pair['Key']
        return None

    def index_collections(self):
        """Fetch the paths to the collections."""
        collections = dict()
        r = self.get('/api/' + self.business)
        soup = BeautifulSoup(r.text, "html.parser")
        for link in soup.findAll('a'):
            collections[link.getText()] = link.get('href')

        return collections

# Below, the indexing of objects, within a collection
    def index_objects(self, collection):
        """Fetch all the paths to the objects in a collection."""
        return self.get(self.collections[collection] + '/index.json').json()

    def index_sales_invoices(self):
        """Fetch all the SalesInvoices."""
        return self.index_objects('SalesInvoice')

    def index_customers(self):
        """Fetch all the Customer indexes."""
        return self.index_objects('Customer')

    def index_cash_accounts(self):
        """Fetch all the cash account indexes."""
        return self.index_objects('CashAccount2')

    def index_tracking_codes(self):
        """Fetch all the Tracking codes indexes."""
        return self.index_objects('TrackingCode')

    def index_profit_loss_account(self):
        """Fetch all the profit and loss accounts indexes."""
        return self.index_objects('ProfitAndLossStatementAccount')

    def index_sales_inventory_items(self):
        """Fetch all the sales invoice items indexes."""
        return self.index_objects('SalesInvoiceItem')

    def index_inventory(self):
        """Fetch all the inventory indexes."""
        return self.index_objects('InventoryItem')

# Below, fetching objects from a collection
    def get_object_thread(self, o_dict, index):
        """A thread function to make fetching objects faster."""
        o_dict[index] = self.get('/api/' + self.business + '/' + index +
                                 '.json').json()
        return

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
            if cnt == 150:
                for thread in threads:
                    threads[thread].join()
                cnt = 0
                threads = dict()

        for thread in threads:
            threads[thread].join()
        return objects

    def get_customers(self):
        """Get all customers."""
        return self.get_objects(self.index_customers())

    def get_sales_invoices(self):
        """Get all Sales Invoices."""
        return self.get_objects(self.index_sales_invoices())

    def get_tracking_codes(self):
        """Get all the tracking codes."""
        return self.get_objects(self.index_tracking_codes())

    def get_cash_accounts(self):
        """Get all cash accounts."""
        return self.get_objects(self.index_cash_accounts())

    def get_profit_loss_accounts(self):
        """Get all accounts in the profit and loss statement."""
        return self.get_objects(self.index_profit_loss_account())

    def get_inventory(self):
        """Get all the inventory Items."""
        return self.get_objects(self.index_inventory())

    def get_sales_inventory_items(self):
        """Get all the sales inventory Items."""
        return self.get_objects(self.index_sales_inventory_items())


# Below, all the PUT commands for the server, to update objects
    def put_object(self, data, object_path):
        """Put an object at that specific path."""
        print('Not yet implemented')
        pass

# Below, all the POST commands for the server, to create objects
    def post(self, data, collection):
        """Post an object at that specific path."""
        print("Posting: ", data, "to: " + self.collections[collection])
        r = self.session.post(self.root_url + self.collections[collection],
                              data=json.dumps(data))

        if r.status_code != 201:
            print('Something went wrong', r.status_code)
            print(collection)
            print(data)

        print("\n\nPost returned data: " + str(r.headers) + '\n')

        return r

    def post_receipt(self, date, debit_account, payer,
                     bank_clear_status, lines):
        """POST to the Receipt collection."""
        data = dict()
        data['Date'] = date
        data['DebitAccount'] = debit_account
        data['Lines'] = lines
        data['Payer'] = payer
        data['BankClearStatus'] = bank_clear_status
        return self.post(data, 'Receipt')

    def post_customer(self, name, email):
        """POST to the Customer collection."""
        data = dict()
        data['Name'] = name
        data['Email'] = email
        data['StartingBalanceType'] = 'Credit'
        return self.post(data, 'Customer')

    def post_sales_invoice(self, issue_date, ref, to, lines):
        """Post to the SalesInvoice collection."""
        data = dict()
        data['IssueDate'] = issue_date
        data['Reference'] = ref
        data['To'] = to
        data['Lines'] = lines
        data['AmountsIncludeTax'] = 'true'
        return self.post(data, 'SalesInvoice')

# Below, all the DEL commands for the server, to delete objects
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
    object_index = gom.index_objects(args.object)
    print(object_index)
    print(gom.get_objects(object_index))

if __name__ == '__main__':
    __main__()
