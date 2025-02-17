import logging
import fairing
import googleapiclient
import httplib2
from fairing.constants import constants

logger = logging.getLogger(__name__)

def configure_http_instance(http=None):
       logger.info("Entering http_utils.py: configure_http_instance({})".format(http))

       if not http:
              http = httplib2.Http()
       
       request_orig = http.request
       user_agent = constants.DEFAULT_USER_AGENT.format(VERSION=fairing.__version__)
       # Reference: https://github.com/googleapis/google-api-python-client/blob/master/googleapiclient/http.py
       # The closure that will replace 'httplib2.Http.request'.
       def append_ua(headers):
              headers = headers or {}
              if 'user-agent' in headers:
                     headers['user-agent'] = user_agent + " " + headers['user-agent']
              else:
                     headers['user-agent'] = user_agent
              return headers

       def new_request(*args, **kwargs):
              """Modify the request headers to add the user-agent."""
              if args and len(args)>=4:
                     args = list(args) 
                     # args is a tuple so assignment is not possible
                     args[3] = append_ua(args[3])
                     args = tuple(args)
              else:
                     kwargs['headers'] = append_ua(kwargs.get('headers'))
              return request_orig(*args, **kwargs)

       http.request = new_request
       logger.info("End http_utils.py: configure_http_instance {}".format(http))
       return http
