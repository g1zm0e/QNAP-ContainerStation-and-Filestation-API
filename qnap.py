import requests
import json
import logging
import re
import xml.etree.ElementTree as ET
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Qnap():
    
    def __init__(self, host, uname, pword):
        self.q_uname = uname
        self.q_pword = pword
        self.q_host = host
        self.auth_cookies = None
        self.sid = None
        self.fs_login = self.fstation_login()
        self.cs_login = self.ctstation_login()
    
    def fstation_login(self):
        login_endpoint = self.fstation_endpoint(
            uri='/authLogin.cgi',
            params={
                'user' : self.q_uname.replace('\\', '+'),
                'pwd' : self.pEncode(self.q_pword)
            }
        )
        response = self.get(login_endpoint, is_xml=True)
        if response is not None:
            xml_root = ET.fromstring(response)
            if xml_root is not None:
                auth_passed = xml_root.find('authPassed').text
                if auth_passed == '1':
                    self.sid = xml_root.find('authSid').text
                    return True
        return False
    
    def ctstation_login(self):
        params = json.dumps(
            {
                'username': self.q_uname, 
                'password': self.q_pword
            }
        )
        login_endpoint = self.ctstation_endpoint(
            '/login',
        )
        response = self.post(login_endpoint, params, func='cookies')
        self.auth_cookies = response
        return True
    
    def base_endpoint(self, uri=None):
        if uri is None:
            endpoint = f'https://{self.q_host}/container-station/api/v1'
        else:
            endpoint = f'https://{self.q_host}/cgi-bin{uri}'
        return endpoint
    
    def ctstation_endpoint(self, uri=None):
        endpoint = self.base_endpoint()
        if uri:
            endpoint = f'{endpoint}{uri}'
        return endpoint
    
    def fstation_endpoint(self, uri='/filemanager/utilRequest.cgi', func=None, params={}):
        endpoint = f'{self.base_endpoint(uri)}?'
        if func:
            endpoint = self.fstation_add_param(endpoint, 'func', func)
        if self.sid:
            endpoint = self.fstation_add_param(endpoint, 'sid', self.sid)
        for key, value in params.items():
            endpoint = self.fstation_add_param(endpoint, key, str(value))
        return endpoint
    
    def fstation_add_param(self, base_url, param, value):
        ret_value = base_url
        if not base_url.endswith('?'):
            ret_value += '&'
        return ret_value + param + '=' + value
    
    def pEncode(self, str):
        ezEncodeChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        out = ''
        length = len(str)
        i = 0
        while i < length:
            c1 = ord(str[i]) & 0xff
            i += 1
            if i == length:
                out += ezEncodeChars[c1 >> 2]
                out += ezEncodeChars[(c1 & 0x3) << 4]
                out += '=='
                break
            c2 = ord(str[i])
            i += 1
            if i == length:
                out += ezEncodeChars[c1 >> 2]
                out += ezEncodeChars[((c1 & 0x3) << 4) | ((c2 & 0xF0) >> 4)]
                out += ezEncodeChars[(c2 & 0xF) << 2]
                out += '='
                break
            c3 = ord(str[i])
            i += 1
            out += ezEncodeChars[c1 >> 2]
            out += ezEncodeChars[((c1 & 0x3)<< 4) | ((c2 & 0xF0) >> 4)]
            out += ezEncodeChars[((c2 & 0xF) << 2) | ((c3 & 0xC0) >> 6)]
            out += ezEncodeChars[c3 & 0x3F]
        return out
    
    def get(self, endpoint, is_xml=None):
        logging.info(f'GET: {endpoint}')
        try:
            if is_xml is None:
                response = requests.get(endpoint, cookies=self.auth_cookies, verify=False)
                if response.status_code != 200:
                    if 'error' in response.json().keys():
                        raise Exception(f'Unable to login to Qnap {self.endpoint}')
            else:
                response = requests.get(endpoint, verify=False)
            return self.get_response_data(response, is_xml)
        except:
            logging.error(f'GET error: {endpoint}')
            return None

    def get_binary(self, endpoint):
        logging.info(f'GET: {endpoint}')
        try:
            response = requests.get(endpoint, verify=False)
        except:
            logging.error(f'GET error: {endpoint}')
            return None
        if self.is_response_binary(response):
            return response.content
        self.get_response_data(response, is_xml=False)
        return None
    
    def post(self, endpoint, data, func=None):
        logging.info(f'url: {endpoint}')
        try:
            response = requests.post(endpoint, data=data, cookies=self.auth_cookies, verify=False)
            if response.status_code != 200 or 'error' in response.json().keys():
                raise Exception(f'Unable to login to Qnap {self.endpoint}')
        except:
            logging.error(f'POST error: {endpoint}')
            return None
        if func == 'cookies':
            cookies = True
            return self.get_response_data(response, cookies=cookies)
        else:
            return self.get_response_data(response)

    def put(self, endpoint):
        logging.info(f'url: {endpoint}')
        try:
            response = requests.put(endpoint, cookies=self.auth_cookies, verify=False)
            if response.status_code != 200:
                raise Exception(f'Unable to login to Qnap {self.endpoint}')
        except:
            logging.error(f'PUT error: {endpoint}')

    def delete(self, endpoint):
        logging.info(f'url: {endpoint}')
        try:
            response = requests.delete(endpoint, cookies=self.auth_cookies, verify=False)
            if response.status_code != 200 or 'error' in response.json().keys():
                raise Exception(f'Unable to login to Qnap {self.endpoint}')
        except:
            logging.error(f'PUT error: {endpoint}')

    
    def get_response_data(self, response, is_xml=None, cookies=False):
        if response.status_code != 200:
            logging.error(f'http status: {response.status_code}')
        if cookies:
            return response.cookies
        elif is_xml == None:
            return response.json()
        elif is_xml:
            return response.text.strip()
        try:
            response_text = response.text.strip()
            # Some responses contain extra content-type header
            response_text = response_text.strip('Content-type: text/html; charset="UTF-8"')
            # Get only first line of output (some responses contain same JSON on 2 different lines)
            match = re.match('.*', response_text)
            if match is not None:
                response_text = match.group(0)
            response_json = json.loads(response_text)
        except:
            return response.content
        return response_json

    def is_response_binary(self, response):
        return 'text/plain' not in response.headers['content-type']

    def jsonprint(self, data):
        """
        Prettify JSON string.
        """
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))