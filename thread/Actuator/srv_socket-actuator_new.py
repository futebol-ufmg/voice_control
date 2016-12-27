# Raspberry PI Actuator
# IP - 192.168.0.37
#Networking
import connection
# argparse to parse the argunments for the logging
import argparse
#Logging
import logging
import vc_logging
import os
#Lamp API
from beautifulhue.api import Bridge

class Actuator():
	"""  

	Actuator node class.

	"""
	def __init__(self, args, HOST = '', PORT = 57000):
		vc_logging.init_logger(level = args.log_level, verbose = args.verbose)
		self.log = logging.getLogger("vc_logger")
		self.HOST = HOST
		self.PORT = PORT
		self.args = args


	def color_to_hue(self, color):
		color_dict = {
						'red'       : 0,
						'yellow'    : 14000,
						'green'     : 25500,
						'blue'      : 47000,
						'pink'      : 56100
					}

		if color == 'white':
			return {'ct' : 153, 'sat': 0}
		else:
			return {'hue' : color_dict[color], 'sat': 254}

	def update_lamp(self, lamp, d):
		#IP: Philips Hue Bridge (the small curcular device that connects to the lamps) IP
		bridge = Bridge(device={'ip': '192.168.0.87'}, user={'name': 'go3D6jUyb3yLQFP0tcPmJ3xzNPIC507T1SL2pnir'})
		resource = {
			'which': lamp,
			'data': {
				'state': d
			}
		}
		bridge.light.update(resource)
		pass

	def convert_command(self, lamp, command):
		
		command_dict = {}
		c = command.split('|')
		

		
		command_dict['on'] = True if c[1] == 'on' else False

		if c[2] == 'all':
			lamp = list(range(1,4))
		else:
			lamp = c[2].split(',')

		if c[3]:
			command_dict.update(self.color_to_hue(c[3]))
		if c[4]:
			command_dict['bri'] = int((int(c[4])/100.0)*254)
		
		return (lamp,command_dict)


	def main(self):
		lamp = 3	#Define default lamp
		
		conn = connection.Server()

		try:
			print 'Opening connection'

			conn.connect()
			conn.accept()

			while True:

				dados = conn.receive_message()

				if dados != None: 

					self.log.info('Received: ' + str(dados))

					data = dados.split('/')

					for d in data:
						if d:
							lamp,command_dict = self.convert_command(lamp, d)
							if command_dict:		#False if command_dict is empty
								for l in lamp:
									print 'lamp:   ' + str(lamp)
									for key,value in command_dict.iteritems():
										print key, value
									self.update_lamp(l, command_dict)
						
							print d
					#CRIA STRING VAZIA NO SPLIT COM VIRGULA SE A VIRGULA ESTA NO FINAL DA STRING ATUAL
			
		except KeyboardInterrupt:
			print '\nINTERRUPTED BY USER'		
		except Exception as e:
			self.log.debug("ERROR: " + str(e))
		finally:
			conn.disconnect()
			conn.destroy()
			self.log.debug('Finishing program')



if(__name__ == '__main__'):
	try:
		parser = argparse.ArgumentParser(description='Actuator Node Logging')
		parser.add_argument('--log-level', action="store", type=str, choices=["critical", "error", "warning", "info", "debug", "notset"], default="info", help='Select the log level of the program.')
		parser.add_argument('--verbose', default=False, action = 'store_true', help='Select whether to output logs to the console.')

		args = parser.parse_args()

	except Exception as e:
		print 'ERROR PARSING ARGUMENTS'
	act = Actuator(args)
	act.main()