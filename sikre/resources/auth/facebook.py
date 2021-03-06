import json
from urllib.parse import parse_qsl

import falcon
import requests

from sikre import settings
from sikre.models.users import User
from sikre.resources.auth import utils
from sikre.utils.logs import logger


class FacebookAuth(object):

    def on_post(self, req, res):

        """Create the JWT token for the user
        """
        access_token_url = 'https://graph.facebook.com/oauth/access_token'
        graph_api_url = 'https://graph.facebook.com/me'

        # Read the incoming data
        stream = req.stream.read()
        data = json.loads(stream.decode('utf-8'))
        logger.debug("Facebook OAuth: Incoming data read successfully")

        params = {
            'client_id': data['clientId'],
            'redirect_uri': data['redirectUri'] + '/',
            'client_secret': settings.FACEBOOK_SECRET,
            'code': data['code']
        }
        logger.debug("Facebook OAuth: Built the code response correctly")

        # Step 1. Exchange authorization code for access token.
        r = requests.get(access_token_url, params=params)
        access_token = dict(parse_qsl(r.text))
        logger.debug("Facebook OAuth: Auth code exchange for token success")

        # Step 2. Retrieve information about the current user.
        r = requests.get(graph_api_url, params=access_token)
        profile = json.loads(r.text)
        logger.debug("Facebook OAuth: Retrieve user information success")

        # Step 3. (optional) Link accounts.
        if req.auth:
            payload = utils.parse_token(req)
            try:
                user = User.select().where(
                    (User.facebook == profile['id']) |
                    (User.id == payload['sub']) |
                    (User.email == profile['email'])
                ).get()
                # Set the facebook code again. This is a failsafe.
                user.facebook = profile['id']
                user.save()
                logger.debug("Facebook OAuth: Account {0} already exists".format(profile["id"]))
            except User.DoesNotExist:
                logger.debug("Facebook OAuth: User does not exist")
                user = User.create(facebook=profile['id'], username=profile['name'], email=profile["email"])
                user.save()
                logger.debug("Facebook OAuth: Created user {0}".format(profile["name"]))
        else:
            try:
                user = User.select().where(
                    (User.facebook == profile['id']) |
                    (User.email == profile['email'])
                ).get()
                # Set the github code again. This is a failsafe.
                user.facebook = profile['id']
                user.save()
            except User.DoesNotExist:
                logger.debug("Facebook OAuth: User does not exist")
                user = User.create(facebook=profile['id'], username=profile['name'], email=profile["email"])
                user.save()
                logger.debug("Facebook OAuth: Created user {0}".format(profile["name"]))
        token = utils.create_jwt_token(user)
        res.body = json.dumps({"token": token})
        res.status = falcon.HTTP_200

    def on_options(self, req, res):

        """Acknowledge the OPTIONS method.
        """
        res.status = falcon.HTTP_200

    def on_get(self, req, res):
        raise falcon.HTTPError(falcon.HTTP_405,
                               title="Client error",
                               description=req.method + " method not allowed.",
                               href=settings.__docs__)

    def on_put(self, req, res):
        raise falcon.HTTPError(falcon.HTTP_405,
                               title="Client error",
                               description=req.method + " method not allowed.",
                               href=settings.__docs__)

    def on_update(self, req, res):
        raise falcon.HTTPError(falcon.HTTP_405,
                               title="Client error",
                               description=req.method + " method not allowed.",
                               href=settings.__docs__)

    def on_delete(self, req, res):
        raise falcon.HTTPError(falcon.HTTP_405,
                               title="Client error",
                               description=req.method + " method not allowed.",
                               href=settings.__docs__)
