"""
.. module::ansicolors
   :platform: Unix
   :synopsis:Class definition for ANSI COLORED Output

.. moduleauthor:: Flavio Ippolito <flavio.ippolito@sm-optics.com>

"""

class bcolors:
	"""
	this class implements the ANSI COLOR escape codes
	"""
	ONBLUE = '\033[34m'
	OKGREEN = '\033[32m'
	WARNING = '\033[33m'
	FAIL = '\033[31m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

def ANSI_warning(str):
	"""
	return str in warning format
	"""
	return bcolors.WARNING + bcolors.BOLD + str + bcolors.ENDC

def ANSI_fail(str):
	"""
	return str in fail format
	"""
	return bcolors.FAIL + bcolors.BOLD + str + bcolors.ENDC

def ANSI_info(str):
	"""
	return str in info format
	"""
	return bcolors.ONBLUE + bcolors.BOLD + str + bcolors.ENDC

def ANSI_success(str):
	"""
	return str in okgreen format
	"""
	return bcolors.OKGREEN + bcolors.BOLD + str + bcolors.ENDC
