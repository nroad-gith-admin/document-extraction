# encoding: utf-8
# Rest api

'''
This module exposes the rest apis.

Available rest api's are:
getType
    Accept Method: POST
    Header: Content-Type: application/json


'''

#!/usr/bin/env python
# coding: utf8

import get_logger

import os
import tornado.ioloop
import tornado.web
from tornado.escape import json_decode
import configparser
from classify import extractData
####################### Config file reading


try:
    debugLevel = 0
    logfilename = "classfier.log"
    ip ="0.0.0.0"
    port = 1998
    parameters = "data"

except Exception as e:
    raise Exception("Config file reading error: "+str(e))

####################### Loggin Functionality

logfilename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "logs", logfilename)
loggerobj = get_logger.GetLogger("Rest",logfilename,debugLevel)
logger = loggerobj.getlogger()

##################### Initializing all the objects

try:
    parameters_req = parameters.split(",")
    parameters_req = [i.strip().lower() for i in parameters_req]

except Exception as e:
    raise Exception(
        "Failed to extract parameters. Parameters should be string separated by quoma ','. failed reason : " + str(e))




###################### Creating Recommendation object
BAD_REQUEST = 400
SUCCESS = 200
INTERNAL_SERVER_ERROR = 500



print("REST API Started")
logger.info("REST API Started")
class REST(tornado.web.RequestHandler):
    def post(self):
        '''
            Accept Method: POST
            Input:
            Output:
            Header: Content-Type: application/json
            :return:
            '''
        ###################### Status Code

        # logger.info("getRecommendation called")
        response = {
            "data": []
        }
        if self.request.method != 'POST':
            logger.error("get-type: Only accept POST request")
            response["status"] = BAD_REQUEST
            response["reason"] = "Only Accept POST request"
            print("Only Accept POST request")
            self.write(response)
            self.set_status(BAD_REQUEST)
        elif not self.request.headers['Content-Type'] == 'application/json':
            logger.error("get-type: Only  Accept Content-Type:application/json")
            response["status"] = BAD_REQUEST
            response["reason"] = "Only  Accept Content-Type:application/json"
            print("Only  Accept Content-Type:application/json")
            self.write(response)
            self.set_status(BAD_REQUEST)
        else:
            try:
                data = json_decode(self.request.body)
            except:
                logger.error(
                    'get-type: Content_Type should be application/json,Expecting json data key as : ' + str(
                        parameters))
                response["status"] = BAD_REQUEST
                response["reason"] = 'Content_Type should be application/json,Expecting json data key as : ' + str(
                    parameters)
                print('Content_Type should be application/json,Expecting json data key as : ' + str(parameters))
                self.write(response)
                self.set_status(BAD_REQUEST)
            else:
                data = dict((k.lower().strip(), v) for k, v in data.items())

                try:
                    for parameter in parameters_req:
                        if parameter not in data.keys():
                            raise Exception()
                except:
                    logger.error("get-type: Expecting key as : " + str(parameters))
                    response["status"] = BAD_REQUEST
                    response["reason"] = 'Expecting key as: ' + str(parameters)
                    print('Expecting key as: ' + str(parameters))
                    self.write(response)
                    self.set_status(BAD_REQUEST)
                else:
                    for idata in data['data']:
                        if "documentId" not in idata or "filePath" not in idata:
                            logger.error("getExtraction: expect documentId and filePath as key")
                            response["status"] = BAD_REQUEST
                            response["reason"] = "Expect documentId and filePath as key"
                            print("Expect documentId and filePath as key")
                            self.write(response)
                            self.set_status(BAD_REQUEST)

                        try:
                            extractedData = extractData(idata["filePath"], idata["documentId"])
                            extractedData["status"] = SUCCESS
                            extractedData["error"] = ""
                            extractedData["documentId"] = idata["documentId"]
                            response["data"].append(extractedData)
                        except Exception as e:
                            extractedData = {}
                            extractedData["status"] = INTERNAL_SERVER_ERROR
                            extractedData["error"] = str(e)
                            extractedData["documentId"] = idata["documentId"]
                            response["data"].append(extractedData)


                    self.write(response)
                    self.set_status(SUCCESS)

application = tornado.web.Application([
    (r"/document-type", REST)
])

if __name__ == "__main__":
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()