#	SDT3PrintOneM2MSVG.py
#
#	Generate SVG in oneM2M's Resource format 


import datetime, os, pathlib, string
from SDT3Classes import *
from SDTSVG import *

# definition of cardinality constants
cardinality1 = '1'
cardinality01 = '0..1'
cardinality0n = '0..n'

# variable that hold an optional header text
headerText = ''


def print3OneM2MSVG(domain, directory, options):
	global headerText

	lfile = options['licensefile']
	if lfile != None:
		with open(lfile, 'rt') as f:
			headerText = f.read()

	# Create package path and make directories

	packagePath = directory + os.sep + domain.id.replace('.', os.sep)
	path = pathlib.Path(packagePath)
	try:
		path.mkdir(parents=True)
	except FileExistsError as e:
		pass # on purpose. We override files for now
	package = sanitizePackage(domain.id)

	# Export ModuleClasses

	for module in domain.modules:
		exportModuleClass(module, package, path)

	# Export Devices

	for device in domain.devices:
		exportDevice(device, package, path)


#############################################################################


# Export a ModuleClass definition to a file

def exportModuleClass(module, package, path, name=None):

	# export the module class itself
	prefix = ''
	if name != None:
		prefix = sanitizeName(name, True) + '_'

	name = sanitizeName(module.name, False)
	fileName = str(path) + os.sep + prefix + name + '.svg'
	outputFile = None
	try:
		outputFile = open(fileName, 'w')
		outputFile.write(getModuleClassSVG(module, package, name, path))		
	except IOError as err:
		print(err)
	finally:
		if (outputFile != None):
			outputFile.close()


# Get the ModuleClass resource

def getModuleClassSVG(module, package, name, path):
	res = Resource(sanitizeName(name, False))
	res.specialization = True

	# TODO: Extends?
	# TODO: events?
	# TODO: actions?

	addModuleClassHeaderToResource(res)

	# DataPoints 
	getDataPoints(res, module.data, name, path)

	addModuleClassFooterToResource(res)

	result  = svgStart(res.width(), res.height(), headerText)
	result += res.draw()
	result += svgFinish()
	return result


# Add standard header attributes to a module class resource

def addModuleClassHeaderToResource(resource):

	contDefinition = Attribute('contDefinition')
	contDefinition.cardinality = cardinality1
	resource.add(contDefinition)

	creator = Attribute('creator')
	creator.cardinality = cardinality01
	resource.add(creator)

	ontologyRef = Attribute('ontologyRef')
	ontologyRef.cardinality = cardinality01
	resource.add(ontologyRef)


# Add standard footer to a module class resource

def addModuleClassFooterToResource(resource):

	subscription = Resource('subscription')
	subscription.cardinality = cardinality0n
	resource.add(subscription)

#############################################################################


# Export a Device definition to a file

def exportDevice(device, package, path):
	name = sanitizeName(device.id, True)
	packagePath = str(path) + os.sep + name.lower()
	path = pathlib.Path(packagePath)

	try:
		path.mkdir(parents=True)
	except FileExistsError as e:
		pass # on purpose. We override files for now

	fileName = str(path) + os.sep + name + '.svg'
	outputFile = None
	try:
		outputFile = open(fileName, 'w')
		outputFile.write(getDeviceSVG(device, package, name))
	except IOError as err:
		print(err)
	finally:
		if (outputFile != None):
			outputFile.close()

	# export module classes of the device

	for module in device.modules:
		exportModuleClass(module, package, path, name)


# Get the Device resource

def getDeviceSVG(device, package, name):
	res = Resource(sanitizeName(name, True))
	res.specialization = True

	addDeviceHeaderToResource(res)

	for module in device.modules:
		mod = Resource(sanitizeName(module.name, True))
		mod.cardinality = cardinality01 if module.optional == 'true' else cardinality1
		mod.specialization = True
		res.add(mod)

	addDeviceFooterToResource(res)

	result  = svgStart(res.width(), res.height(), headerText)
	result += res.draw()
	result += svgFinish()
	return result


# Add standard header attributes to a device resource

def addDeviceHeaderToResource(resource):

	contDefinition = Attribute('contDefinition')
	contDefinition.cardinality = cardinality1
	resource.add(contDefinition)

	creator = Attribute('creator')
	creator.cardinality = cardinality01
	resource.add(creator)

	ontologyRef = Attribute('ontologyRef')
	ontologyRef.cardinality = cardinality01
	resource.add(ontologyRef)

	subscription = Resource('deviceProperty')
	subscription.cardinality = cardinality01
	subscription.specialization = True
	resource.add(subscription)



# Add standard footer to a device resource

def addDeviceFooterToResource(resource):

	subscription = Resource('subscription')
	subscription.cardinality = cardinality0n
	subscription.specialization = False
	resource.add(subscription)

#############################################################################

# Export a DataPoint definiton to a file

def exportDataPoint(dataPoint, moduleName, path):
	name = sanitizeName(dataPoint.name, True)
	mName = sanitizeName(moduleName, True)
	fileName = str(path) + os.sep + mName + '_' + name + '.svg'
	outputFile = None
	try:
		outputFile = open(fileName, 'w')
		outputFile.write(getDataPointSVG(dataPoint))		
	except IOError as err:
		print(err)
	finally:
		if (outputFile != None):
			outputFile.close()


# Get the DataPoint resource

def getDataPointSVG(dataPoint):
	res = Resource(sanitizeName(dataPoint.name, False))
	res.specialization = True

	addDataPointHeaderToResource(res)
	# Nothing in between
	addDataPointFooterToResource(res)

	result  = svgStart(res.width(), res.height(), headerText)
	result += res.draw()
	result += svgFinish()
	return result


# Construct data points export
def getDataPoints(resource, dataPoints, moduleName, path):
	if (dataPoints == None or len(dataPoints) == 0):
		return
	for dataPoint in dataPoints:

		# First add it to the resource

		dp = Attribute(sanitizeName(dataPoint.name, False))

		if (dataPoint.optional == 'true'):
			dp.cardinality = cardinality01
		else:
			dp.cardinality = cardinality1
		resource.add(dp)

		# write out to a file
		exportDataPoint(dataPoint, moduleName, path)



# Add standard header attributes to a device resource

def addDataPointHeaderToResource(resource):

	contDefinition = Attribute('contDefinition')
	contDefinition.cardinality = cardinality1
	resource.add(contDefinition)

	creator = Attribute('creator')
	creator.cardinality = cardinality01
	resource.add(creator)

	ontologyRef = Attribute('ontologyRef')
	ontologyRef.cardinality = cardinality01
	resource.add(ontologyRef)


# Add standard footer to a device resource

def addDataPointFooterToResource(resource):

	subscription = Resource('subscription')
	subscription.cardinality    = cardinality0n
	subscription.specialization = False
	resource.add(subscription)

########################################################################


#
#	Helpers
#

# Sanitize the name for Vorto

def sanitizeName(name, isClass):
	if (name == None or len(name) == 0):
		return ''
	result = name
	if (isClass):
		result = result[0].upper() + name[1:]
	else:
		result = result[0].lower() + name[1:]
	result = result.replace(' ', '')
	result = result.replace('/', '')
	result = result.replace('.', '')
	result = result.replace(' ', '')
	result = result.replace("'", '')
	result = result.replace('´', '')
	result = result.replace('`', '')
	result = result.replace('(', '_')
	result = result.replace(')', '_')
	result = result.replace('-', '_')

	return result

# Sanitize the package name for Java

def sanitizePackage(package):
	result = package.replace('/', '.')
	return result

def soundex(name, len=4):
	""" soundex module conforming to Knuth's algorithm
		implementation 2000-12-24 by Gregory Jorgensen
		public domain
		"""

	# digits holds the soundex values for the alphabet
	digits = '01230120022455012623010202'
	# alternative: digits = '01230120002055012623010202'
	sndx = ''
	fc = ''

	# translate alpha chars in name to soundex digits
	for c in name.upper():
		if c.isalpha():
			if not fc: fc = c   # remember first letter
			d = digits[ord(c)-ord('A')]
			# duplicate consecutive soundex digits are skipped
			if not sndx or (d != sndx[-1]):
				sndx += d

	# replace first digit with first alpha character
	sndx = fc + sndx[1:]

	# remove all 0s from the soundex code
	sndx = sndx.replace('0','')

	# return soundex code padded to len characters
	return (sndx + (len * '0'))[:len]


# experimental abreviation function. Move later

def abbreviate(name, length=5):
	l = len(name)
	if l <= length:
		result = name
		while l < length:
			for i in range(length - l):
				result += result[i]
			l = len(result)
		return result.upper()
	
	# First char
	result  = name[0]
	
	# Last char
	result += name[-1]

	if len(result) < length:
		mask = name[1:l-1]
		# Camel cases chars
		camels = ''
		for i in range(1,l-1):
			c = name[i]
			if c.isupper():
				camels += c
				mask = mask[:i-1] + mask[i:]
		result = result[:1] + camels + result[1:]

		# Fill with remaining chars of the mask, starting from the back
		lm = len(mask)
		for i in range(0, length - len(result)):
			pos = i + 1
			result = result[:pos] + mask[i] + result[pos:] 

	return result[:length].upper()








