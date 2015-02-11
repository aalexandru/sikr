#!/usr/bin/env python

# Copyright 2014 Clione Software and Havas Worldwide London
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sys
import time
import os
import getpass
# path = os.path.dirname(os.path.realpath(__file__)).strip('/utils')
# sys.path.append(path)
# print(sys.path)
import hashlib
import uuid
import random
import string

from peewee import *


from sikre.models.models import User, Item, Service, ItemGroup


def send_message(string):
    print(string, end='\r')
    sys.stdout.write("\033[K")
    #time.sleep(0.3)
    #print("\r" * len(string), end='')

############################
# Admin user creation      #
############################

create_admin = input("\nDo you want to create an admin user? (Y/n) ")
if create_admin in ['y', 'Y', 'yes', 'YES', None]:
    name = input("Full name: ")
    email = input("E-Mail address: ")
    username = input("Username (no spaces): ")
    password = getpass.getpass("Password (we don't ask twice!): ")

    # Process the password for storage
    salt = uuid.uuid4().hex.encode('utf-8')
    hashed_password = hashlib.sha512(password.encode('utf-8') + salt).hexdigest()

    # Create the user object in the database
    new_user = User.create(name=name, email=email, username=username,
                           password=hashed_password, token='dummytoken',
                           is_superuser=True)
    user = new_user.save()
else:
    print("Admin user not created. You can create it afterwards.\n")


##########################
# Database generation    #
##########################

# Create a dummy user if there's no admin
if create_admin != 'y' and create_admin != 'Y':
    new_user = User.create(name="Dummy", email="dummy@example.com",
                           username="dummy", password="dummy", token="dummy")
    user = new_user.save()

# Create a secondary user
secondary_user = User.create(name="Second", email="example@example.com",
                             username="second", password="second", token="dummy1")
secondary_user.save()
# Create some groups
groups = 5
while groups > 0:
    send_message(" * Creating groups, {0} remaining".format(groups))
    chars = "".join([random.choice(string.ascii_letters) for i in range(10)])
    new_group = ItemGroup.create(name=chars,)
    new_group.save()
    groups -= 1

    # Create some items
    items = 10
    while items > 0:
        send_message(" * Creating items for group {0}. {1} remaining".format(new_group.id, items))
        chars = "".join([random.choice(string.ascii_letters) for i in range(15)])
        digits = "".join([random.choice(string.digits) for i in range(8)])
        new_item = Item(name=chars, description=chars * 2, group=new_group)
        new_item.save()
        new_item.allowed_users.add(random.choice([new_user, secondary_user]))
        items -= 1

        # Create some services
        services = 4
        while services > 0:
            send_message(" * Creating services for item {0}. {1} remaining".format(new_item.id, services))
            chars = "".join([random.choice(string.ascii_letters) for i in range(15)])
            digits = "".join([random.choice(string.digits) for i in range(8)])
            new_service = Service(name=chars, username=chars, password=chars, url=chars,
                                  item=new_item)
            new_service.save()
            services -= 1
print(" * Database generation completed successfully")
