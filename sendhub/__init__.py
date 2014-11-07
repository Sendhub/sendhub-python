# -*- coding: utf-8 -*-

# SendHub Python bindings

## Imports
import logging
import re
import platform
import sys
import urllib
import urlparse
import textwrap
import datetime
import requests
from version import VERSION
import simplejson as json
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

_httplib = 'requests'

logger = logging.getLogger('sendhub')

## Configuration variables
userName = None
password = None
internalApi = False
apiBase = 'https://api.sendhub.com'
entitlementsBase = 'https://entitlements.sendhub.com'
profileBase = 'https://profile.sendhub.com'
billingBase = 'https://billing.sendhub.com'
apiVersion = None


## Exceptions
class SendHubError(Exception):
    def __init__(
            self, message=None, devMessage=None, code=None, moreInfo=None):
        super(SendHubError, self).__init__(message)
        self.devMessage = devMessage.decode('utf-8') \
            if devMessage is not None else ''
        self.code = code if code is not None else -1
        self.moreInfo = moreInfo.decode('utf-8') \
            if moreInfo is not None else ''

_underscorer1 = re.compile(r'(.)([A-Z][a-z]+)')
_underscorer2 = re.compile('([a-z0-9])([A-Z])')

def camelToSnake(s):
    """
    Is it ironic that this function is written in camel case, yet it
    converts to snake case? hmm..
    """
    subbed = _underscorer1.sub(r'\1_\2', s)
    return _underscorer2.sub(r'\1_\2', subbed).lower()

class APIError(SendHubError):
    pass


class APIConnectionError(SendHubError):
    pass


class EntitlementError(SendHubError):
    def __init__(self, message, devMessage=None, code=None, moreInfo=None):
        super(EntitlementError, self).__init__(
            message, devMessage, code, moreInfo)


class InvalidRequestError(SendHubError):
    def __init__(self, message, devMessage=None, code=None, moreInfo=None):
        super(InvalidRequestError, self).__init__(
            message, devMessage, code, moreInfo)


class AuthenticationError(SendHubError):
    pass

class AuthorizationError(SendHubError):
    pass


def convertToSendhubObject(resp):
    types = {'entitlement': Entitlement}

    if isinstance(resp, list):
        return [convertToSendhubObject(i) for i in resp]
    elif isinstance(resp, dict):
        resp = resp.copy()
        klassName = resp.get('object')
        if isinstance(klassName, basestring):
            klass = types.get(klassName, SendHubObject)
        else:
            klass = SendHubObject
        return klass.constructFrom(resp)
    else:
        return resp

## Network transport
class APIRequestor(object):

    apiBase = None

    def apiUrl(self, url=''):
        return '%s%s/' % \
               (self.apiBase if self.apiBase is not None else apiBase, url)

    @classmethod
    def _utf8(cls, value):
        if isinstance(value, unicode) and sys.version_info < (3, 0):
            return value.encode('utf-8')
        else:
            return value

    @classmethod
    def encodeDatetime(cls, dttime):
        return dttime.strftime('%Y-%m-%dT%H:%M:%S')

    @classmethod
    def encode_list(cls, listvalue):
        # only supports lists of things that can be represented as strings
        return ','.join(map(str, listvalue))

    @classmethod
    def _encodeInner(cls, d):
        # special case value encoding
        ENCODERS = {
            list: cls.encode_list,
            datetime.datetime: cls.encodeDatetime
        }

        stk = {}
        for key, value in d.iteritems():
            key = cls._utf8(key)
            try:
                encoder = ENCODERS[value.__class__]
                stk[key] = encoder(value)
            except KeyError:
                # don't need special encoding
                value = cls._utf8(value)
                stk[key] = value
        return stk

    @classmethod
    def encode(cls, d):
        """
        Internal: encode a string for url representation
        """
        return urllib.urlencode(cls._encodeInner(d))

    @classmethod
    def encodeJson(cls, d):
        """
        Internal: encode a string for url representation
        """
        return json.dumps(cls._encodeInner(d))

    @classmethod
    def buildUrl(cls, url, params, authParamsOnly=False):

        if authParamsOnly:

            newParams = {}

            for param in params:
                if (param == 'username' or param == 'password'
                        or param == 'apiUsername' or param == 'apiPassword'):
                    newParams[param] = params[param]
            params = newParams


        baseQuery = urlparse.urlparse(url).query
        if baseQuery:
            return '%s&%s' % (url, cls.encode(params))
        else:
            return '%s?%s' % (url, cls.encode(params))

    def request(self, meth, url, params={}):
        rbody, rcode = self.performRequest(meth, url, params)
        resp = self.interpretResponse(rbody, rcode)
        return resp

    def handleApiError(self, rbody, rcode, resp):
        try:
            # message is required
            message = resp['message']
        except (KeyError, TypeError):
            raise APIError(
                "Invalid response object from API: %r (HTTP response code "
                "was %d)" % (rbody, rcode), '', rcode, '')

        if 'devMessage' in resp:
            devMessage = resp['devMessage']
        else:
            devMessage = ''

        if 'code' in resp:
            code = resp['code']
        else:
            code = -1

        if 'moreInfo' in resp:
            moreInfo = resp['moreInfo']
        else:
            moreInfo = ''

        if rcode in [400, 404]:
            raise InvalidRequestError(message, devMessage, code, moreInfo)
        elif rcode == 401:
            raise AuthenticationError(message, devMessage, code, moreInfo)
        elif rcode == 403:
            raise AuthorizationError(message, devMessage, code, moreInfo)
        else:
            raise APIError(message, devMessage, code, moreInfo)

    def performRequest(self, meth, url, params={}):
        """
        Mechanism for issuing an API call
        """
        if userName is None or password is None:
            raise AuthenticationError('No authentication details provided')

        absUrl = self.apiUrl(url)
        params = params.copy()
        if internalApi:
            params['apiUsername'] = userName
            params['apiPassword'] = password
        else:
            params['username'] = userName
            params['api_key'] = password

        ua = {
            'bindingsVersion': VERSION,
            'lang': 'python',
            'publisher': 'sendhub',
            'httplib': _httplib,
        }
        for attr, func in [['langVersion', platform.python_version],
                           ['platform', platform.platform],
                           ['uname', lambda: ' '.join(platform.uname())]]:
            try:
                val = func()
            except Exception, e:
                val = "!! %s" % e
            ua[attr] = val

        headers = {
            'Content-Type': 'application/json',
            'X-SendHub-Client-User-Agent': json.dumps(ua),
            'User-Agent': 'SendHub/v1 PythonBindings/%s' % (VERSION, )
        }
        if apiVersion is not None:
            headers['SendHub-Version'] = apiVersion

        rbody, rcode = self.doSendRequest(meth, absUrl, headers, params)

        logger.info(
            'API request to %s returned (response code, response body) '
            'of (%d, %r)' % (absUrl, rcode, rbody))

        return rbody, rcode

    def interpretResponse(self, rbody, rcode):

        # special case deleted because the response is empty
        if rcode == 204:
            resp = {
                'message' : 'OK'
            }
            return resp

        try:
            resp = json.loads(rbody.decode('utf-8'))
        except Exception:
            raise APIError(
                "Invalid response body from API: %s (HTTP response code "
                "was %d)" % (rbody, rcode), '', rcode)
        if not (200 <= rcode < 300):
            self.handleApiError(rbody, rcode, resp)
        return resp

    def doSendRequest(self, meth, absUrl, headers, params):
        meth = meth.lower()
        if meth == 'get' or meth == 'delete':
            if params:
                absUrl = self.buildUrl(absUrl, params)
            data = None
        elif (meth == 'post' or meth == 'put'):
            absUrl = self.buildUrl(absUrl, params, True)

            newParams = {}
            for param in params:
                if (param != 'username' and param != 'password'
                        and param != 'apiUsername' and param != 'apiPassword'):
                    newParams[param] = params[param]
            params = newParams

            data = self.encodeJson(params)
        else:
            raise APIConnectionError(
                'Unrecognized HTTP method %r.  This may indicate a bug '
                'in the SendHub bindings.  Please contact support@sendhub.com '
                'for assistance.' % (meth, ))

        kwargs = {}
        try:
            try:
                result = requests.request(meth, absUrl,
                                          headers=headers, data=data,
                                          timeout=80,
                                          **kwargs)
            except TypeError, e:
                raise TypeError(
                    'Warning: It looks like your installed version of the '
                    '"requests" library is not compatible. The underlying '
                    'error was: %s' % (e, ))

            content = result.content
            statusCode = result.status_code
        except Exception, e:
            self.handleRequestError(e)
        return content, statusCode

    def handleRequestError(self, e):
        if isinstance(e, requests.exceptions.RequestException):
            msg = "Unexpected error communicating with SendHub.  If this " \
                  "problem persists, let us know at support@sendhub.com."
            err = "%s: %s" % (type(e).__name__, str(e))
        else:
            msg = "Unexpected error communicating with SendHub.  It looks " \
                  "like there's probably a configuration issue locally.  " \
                  "If this problem persists, let us know at " \
                  "support@sendhub.com."
            err = "A %s was raised" % (type(e).__name__, )
            if str(e):
                err += " with error message %s" % (str(e), )
            else:
                err += " with no error message"
        msg = textwrap.fill(msg) + "\n\n(Network error: " + err + ")"
        raise APIConnectionError(msg)


class SendHubObject(object):
    def __init__(self, id=None, **params):
        self.__dict__['_values'] = set()


    def __setattr__(self, k, v):
        self.__dict__[k] = v
        self._values.add(k)


    def __getattr__(self, k):
        try:
            return self.__dict__[k]
        except KeyError:
            pass


    def __getitem__(self, k):
        if k in self._values:
            return self.__dict__[k]
        else:
            raise KeyError(k)


    def get(self, k, default=None):
        try:
            return self[k]
        except KeyError:
            return default


    def setdefault(self, k, default=None):
        try:
            return self[k]
        except KeyError:
            self[k] = default
            return default


    def __setitem__(self, k, v):
        setattr(self, k, v)


    def keys(self):
        return self.toDict().keys()


    def values(self):
        return self.toDict().values()


    @classmethod
    def constructFrom(cls, values):
        instance = cls(values.get('id'))
        instance.refreshFrom(values)
        return instance


    def refreshFrom(self, values):

        for k, v in values.iteritems():
            name = camelToSnake(k)
            self.__dict__[name] = convertToSendhubObject(v)
            self._values.add(name)


    def __repr__(self):
        typeString = ''
        if isinstance(self.get('object'), basestring):
            typeString = ' %s' % self.get('object').encode('utf8')

        idString = ''
        if isinstance(self.get('id'), basestring):
            idString = ' id=%s' % self.get('id').encode('utf8')

        return '<%s%s%s at %s> JSON: %s' % (
        type(self).__name__, typeString, idString, hex(id(self)),
        json.dumps(self.toDict(), sort_keys=True, indent=2,
                   cls=SendHubObjectEncoder))


    def __str__(self):
        return json.dumps(self.toDict(), sort_keys=True, indent=2,
                          cls=SendHubObjectEncoder)


    def toDict(self):
        def _serialize(o):
            if isinstance(o, SendHubObject):
                return o.toDict()
            if isinstance(o, list):
                return [_serialize(i) for i in o]
            return o

        d = dict()
        for k in sorted(self._values):
            v = getattr(self, k)
            v = _serialize(v)
            d[k] = v
        return d


class SendHubObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, SendHubObject):
            return obj.toDict()
        else:
            return json.JSONEncoder.default(self, obj)


class APIResource(SendHubObject):

    def getBaseUrl(self):
        return apiBase

    def get_object(self, obj_id):
        requestor = APIRequestor()
        requestor.apiBase = self.getBaseUrl()
        url = self.instanceUrl(str(obj_id))
        response = requestor.request('get', url)
        self.refreshFrom(response)
        self.id = obj_id
        return self

    def get_list(self):
        requestor = APIRequestor()
        requestor.apiBase = self.getBaseUrl()
        response = requestor.request('get', self.classUrl())
        return [SendHubObject.constructFrom(i) for i in response]

    def create_object(self, **params):

        requestor = APIRequestor()
        requestor.apiBase = self.getBaseUrl()
        url = self.classUrl()
        response = requestor.request('post', url, params)
        self.refreshFrom(response)

        return self

    def update_object(self, obj_id, **params):

        requestor = APIRequestor()
        requestor.apiBase = self.getBaseUrl()
        url = self.instanceUrl(str(obj_id))
        response = requestor.request('put', url, params)
        self.refreshFrom(response)
        self.id = obj_id

        return self

    @classmethod
    def className(cls):
        if cls == APIResource:
            raise NotImplementedError('APIResource is an abstract class.')
        return "%s" % urllib.quote_plus(cls.__name__.lower())

    @classmethod
    def classUrl(cls):
        clsname = cls.className()
        return "/v1/%ss" % clsname

    def instanceUrl(self, id=None):
        id = self.get('id') if id is None else id
        if not id:
            raise InvalidRequestError(
                'Could not determine which URL to request: %s instance has '
                'invalid ID: %r' % (type(self).__name__, id), 'id')
        id = APIRequestor._utf8(id)
        base = self.classUrl()
        extn = urllib.quote_plus(id)
        return "%s/%s" % (base, extn)

# API objects
class Entitlement(APIResource):

    def getBaseUrl(self):
        return entitlementsBase

    def listUsage(self, userId):
        requestor = APIRequestor()
        requestor.apiBase = self.getBaseUrl()
        url = self.instanceUrl(str(userId))
        response = requestor.request('get', url)
        self.refreshFrom(response)
        return self

    def check(self, userId, action, **params):
        requestor = APIRequestor()
        requestor.apiBase = self.getBaseUrl()
        url = self.instanceUrl(str(userId)) + '/' + str(action)
        response = requestor.request('get', url, params)
        self.refreshFrom(response)

        return self

    def update(self, userId, action, **params):

        try:
            requestor = APIRequestor()
            requestor.apiBase = self.getBaseUrl()
            url = self.instanceUrl(str(userId)) + '/' + str(action)
            response = requestor.request('post', url, params)
            self.refreshFrom(response)

            self.id = self.uuid
        except AuthorizationError as e:
            raise EntitlementError(e.message, e.devMessage, e.code, e.moreInfo)

        return self

    def confirmUpdate(self):
        if self.id is None:
            raise InvalidRequestError('An id(uuid) must be set prior '
                                      'to confirming')

        requestor = APIRequestor()
        requestor.apiBase = self.getBaseUrl()
        url = self.instanceUrl(str(self.userId)) + '/' + str(self.action) \
              + '/' + str(self.id)
        response = requestor.request('post', url)
        self.refreshFrom(response)

        self.id = self.uuid

        return self

    def reset(self, userId, action, **params):
        requestor = APIRequestor()
        requestor.apiBase = self.getBaseUrl()
        url = self.instanceUrl(str(userId)) + '/' + str(action)
        response = requestor.request('delete', url)
        self.refreshFrom(response)

        return self

    def resetAll(self, userId, **params):
        requestor = APIRequestor()
        requestor.apiBase = self.getBaseUrl()
        url = self.instanceUrl(str(userId))
        response = requestor.request('delete', url)
        self.refreshFrom(response)

        return self

class EntitlementV2(APIResource):

    def getBaseUrl(self):
        return entitlementsBase

    def list_usage(self, enterprise_id):
        requestor = APIRequestor()
        requestor.apiBase = self.getBaseUrl()
        url = self.instanceUrl(str(enterprise_id))
        response = requestor.request('get', url)
        self.refreshFrom(response)
        return self

    def list_limits(self, enterprise_id):
        requestor = APIRequestor()
        requestor.apiBase = self.getBaseUrl()
        url = '{}/limits'.format(self.instanceUrl(str(enterprise_id)))
        response = requestor.request('get', url)
        self.refreshFrom(response)
        return self

    def check(self, enterprise_id, user_id, action, **params):
        requestor = APIRequestor()
        requestor.apiBase = self.getBaseUrl()
        url = '{}/{}/{}'.format(
            self.instanceUrl(str(enterprise_id)), str(user_id), str(action))
        response = requestor.request('get', url, params)
        self.refreshFrom(response)

        return self

    def update(self, enterprise_id, user_id, action, **params):

        try:
            requestor = APIRequestor()
            requestor.apiBase = self.getBaseUrl()
            url = '{}/{}/{}'.format(
                self.instanceUrl(str(enterprise_id)),
                str(user_id),
                str(action))
            response = requestor.request('post', url, params)
            self.refreshFrom(response)
        except AuthorizationError as e:
            raise EntitlementError(e.message, e.devMessage, e.code, e.moreInfo)

        return self

    def reset(self, enterprise_id, **params):
        requestor = APIRequestor()
        requestor.apiBase = self.getBaseUrl()
        url = self.instanceUrl(str(enterprise_id))
        response = requestor.request('delete', url)
        self.refreshFrom(response)

        return self

    def update_limit(self, enterprise_id, limit, value, **params):

        try:
            requestor = APIRequestor()
            requestor.apiBase = self.getBaseUrl()
            url = '{}/limits/{}/{}'.format(
                self.instanceUrl(str(enterprise_id)),
                str(limit),
                str(value))
            response = requestor.request('post', url, params)
            self.refreshFrom(response)

        except AuthorizationError as e:
            raise EntitlementError(e.message, e.devMessage, e.code, e.moreInfo)

        return self

    @classmethod
    def classUrl(cls):
        return "/api/v2/entitlements"

class Profile(APIResource):

    def getBaseUrl(self):
        return profileBase

    def get_user(self, user_id):
        return self.get_object(user_id)

    @classmethod
    def classUrl(cls):
        clsname = cls.className()
        return "/api/v3/%ss" % clsname

class BillingAccount(APIResource):

    def getBaseUrl(self):
        return billingBase

    def get_account(self, enterprise_id):
        return self.get_object(enterprise_id)

    def create_account(
            self,
            enterprise_id,
            enterprise_name,
            plan_id,
            count,
            customer_id=None):

        return self.create_object(
            id=enterprise_id,
            name=enterprise_name,
            planId=str(plan_id),
            subscriptionCount=count,
            customer=customer_id)

    def delete_account(self, enterprise_id):
        requestor = APIRequestor()
        requestor.apiBase = self.getBaseUrl()
        url = self.instanceUrl(str(enterprise_id))
        requestor.request('delete', url)

    def change_plan(self, enterprise_id, plan_id):
        return self.update_object(
            obj_id=enterprise_id,
            id=enterprise_id,
            planId=str(plan_id))

    def add_user(self, enterprise_id, count=1):
        requestor = APIRequestor()
        requestor.apiBase = self.getBaseUrl()
        url = '{}/users'.format(self.instanceUrl(str(enterprise_id)))
        response = requestor.request('post', url, {'subscriptionCount': count})
        self.refreshFrom(response)

        return self

    def delete_user(self, enterprise_id):
        requestor = APIRequestor()
        requestor.apiBase = self.getBaseUrl()
        url = '{}/users'.format(self.instanceUrl(str(enterprise_id)))
        requestor.request('delete', url)

    def get_payment_data(self, enterprise_id):
        requestor = APIRequestor()
        requestor.apiBase = self.getBaseUrl()
        url = '{}/subscription'.format(
            self.instanceUrl(str(enterprise_id)))
        response = requestor.request('get', url)
        self.refreshFrom(response)

        return self

    def adjust_balance(
            self,
            enterprise_id,
            balance_adjustment,
            adjustment_type,
            description
    ):
        requestor = APIRequestor()
        requestor.apiBase = self.getBaseUrl()
        url = '{}/balance'.format(
            self.instanceUrl(str(enterprise_id))
        )
        response = requestor.request(
            'put',
            url,
            {
                'balanceAdjustment': balance_adjustment,
                'adjustmentType': adjustment_type,
                'description': description
            }
        )
        self.refreshFrom(response)

        return response

    def get_plan_data(self, enterprise_id):
        requestor = APIRequestor()
        requestor.apiBase = self.getBaseUrl()
        url = '{}/plan'.format(
            self.instanceUrl(str(enterprise_id)))
        response = requestor.request('get', url)
        self.refreshFrom(response)

        return self

    @classmethod
    def classUrl(cls):
        return "/api/v2/accounts"


class BillingPlans(APIResource):

    def getBaseUrl(self):
        return billingBase

    def list_plans(self):
        return self.get_list()

    def get_plan(self, plan_id):
        return self.get_object(plan_id)

    @classmethod
    def classUrl(cls):
        return "/api/v2/plans"