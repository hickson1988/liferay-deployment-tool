import subprocess
import urllib.request
import time
import sys
import configparser

def serverIsUp(config):
	try:
		server_url=config['GeneralConfig']['ServerUrl']
		if  urllib.request.urlopen(server_url).getcode()==200:
			print("Server is up")
			return True						
		else:
			print("Server is not responding")
			return False
	except:
		print("Server is down or something else went wrong")
		return False

def deployExt(config):
	try:
		ext_to_deploy=config['ExtToDeploy']['module']		
		plugins_sdk_path=config['GeneralConfig']['PluginsSdkPath']
		
		if not ext_to_deploy == "":
			print("Deploying ext...")
			test = subprocess.check_call('ant clean direct-deploy', cwd=plugins_sdk_path+'\ext\\'+ext_to_deploy,shell=True,universal_newlines=True)
			print('Building ext...')
			if test==0:
		 		print('Ext Build succesful')
	except:   
	 	print('Ext Build error')      
	 	print("Unexpected error:", sys.exc_info()[0])
	 	raise

def startServer(config):
	try:		
		print('Starting server...')   		
		tomcat=config['GeneralConfig']['TomcatPath']
		cygwin_link_name=config['CygwinConfig']['CygwinLinkName']
		cygwin_link_path=config['CygwinConfig']['CygwinLinkPath']

		if config['CygwinConfig']['StartServerFromCygwin'] == 'True':
			subprocess.Popen(cygwin_link_name, cwd=cygwin_link_path,shell=True,universal_newlines=True)	 
		else:
			subprocess.Popen('startup.bat', cwd=tomcat+'\\bin',shell=True,universal_newlines=True)	
		time.sleep(5)
		waitForServerToOpen(config)		
	except:  
	 	print('Server startup error error')                                                                                                
	 	print("Unexpected error:", sys.exc_info()[0])
	 	raise

def waitForServerToOpen(config):
	print('Waiting for server to open...')  
	while True:		 
		try:
			server_url=config['GeneralConfig']['ServerUrl']
			response_code=urllib.request.urlopen(server_url).getcode()

			if response_code==200:
				print("Server up!")
				break
			else:
				print("Server not responding. Will ping in 5 seconds again to check.")	
		except:
			print("Server is down")
		time.sleep(3)

def waitForServerToStop(config):
	print('Waiting for server to stop...')  
	while True:
		try:
			time.sleep(3)
			server_url=config['GeneralConfig']['ServerUrl']
			response_code=urllib.request.urlopen(server_url).getcode()

			if response_code!=200:
				print("Server is down")
				break
			else:
				print("Server not responding. Will ping in 5 seconds again to check.")	
		except:
			print("Server is down")
			break

def stopServer(config):
	try:
		print("Closing server...")
		tomcat=config['GeneralConfig']['TomcatPath']
		test=subprocess.check_call('shutdown.bat', cwd=tomcat+'\\bin',shell=True,universal_newlines=True)						
		waitForServerToStop(config)

		if test==0:			
			print("Server closed succesfully.")		
	except: 
		print('Error closing server.')                                                                                                
		print("Unexpected error:", sys.exc_info()[0])
		raise

def redeployHook(config):
	
	plugins_sdk_path=config['GeneralConfig']['PluginsSdkPath']
	tomcat=config['GeneralConfig']['TomcatPath']
	hooks_to_deploy=config['HooksToDeploy']['modules'].split(',')

	for hook in hooks_to_deploy:
		if not hook == '': 
			undeploy=config['HooksToDeploy']['undeploy']
			if undeploy == 'True':
				try:
					test=subprocess.check_call('rmdir '+hook+' /s /q', cwd=tomcat+'\\webapps',shell=True,universal_newlines=True)						
					if test==0:			
						print(hook+" hook undeployed.")		
				except: 
					print(hook+" hook is not deployed on server")

			print("Deploying "+hook+"...")	

			test=subprocess.check_call('ant all', cwd=plugins_sdk_path+'\hooks\\'+hook,shell=True,universal_newlines=True)						
			if test==0:			
				print(hook+"hook deployed.")	

def deployPortlets(config):
	plugins_sdk_path=config['GeneralConfig']['PluginsSdkPath']
	tomcat=config['GeneralConfig']['TomcatPath']
	portlets_to_deploy=config['PortletsToDeploy']['modules'].split(',')
	
	for portlet in portlets_to_deploy:
		if not portlet == '': 
			undeploy=config['PortletsToDeploy']['undeploy']
			
			if undeploy == 'True':
				try:
					test=subprocess.check_call('rmdir '+portlet+' /s /q', cwd=tomcat+'\\webapps',shell=True,universal_newlines=True)						
					if test==0:			
						print(portlet+"portlet undeployed.")		
				except: 
					print(portlet+"portlet is not deployed on server")

			test=subprocess.check_call('ant all', cwd=plugins_sdk_path+'\portlets\\'+portlet,shell=True,universal_newlines=True)	
			if test==0:			
				print(portlet+" portlet deployed.")		
			time.sleep(3)

def deployThemes(config):
	plugins_sdk_path=config['GeneralConfig']['PluginsSdkPath']
	tomcat=config['GeneralConfig']['TomcatPath']
	themes_to_deploy=config['ThemesToDeploy']['modules'].split(',')
	
	for theme in themes_to_deploy:
		if not theme == '': 
			undeploy=config['ThemesToDeploy']['undeploy']
		
			if undeploy == 'True':
				try:
					test=subprocess.check_call('rmdir '+theme+' /s /q', cwd=tomcat+'\\webapps',shell=True,universal_newlines=True)						
					if test==0:			
						print(theme+"theme undeployed.")		
				except: 
					print(theme+"theme is not deployed on server")

			test=subprocess.check_call('ant all', cwd=plugins_sdk_path+'\\themes\\'+theme,shell=True,universal_newlines=True)	
			if test==0:			
				print(theme+" theme deployed.")		
			time.sleep(3)


def deployAll(config):

	ext=config['ExtToDeploy']['module'];

	if serverIsUp(config) and not ext == "":
		stopServer(config)
		deployExt(config)
		time.sleep(3)
	elif not serverIsUp(config) and not ext == "":
		deployExt(config)
		time.sleep(3)

	if not serverIsUp(config):
		startServer(config)

	time.sleep(3)
	redeployHook(config)

	time.sleep(3)
	deployThemes(config)
	
	time.sleep(3)
	deployPortlets(config)


config = configparser.ConfigParser()
config.read("config.ini")

deployAll(config)








