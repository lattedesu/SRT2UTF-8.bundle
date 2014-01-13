# Convert sidecar subtitle files files into UTF-8 format
# Created by dane22, a Plex community member
#


######################################### Global Variables #########################################
sVersion = '0.0.1.0'
sTitle = 'SRT2UTF-8'

######################################### Imports ##################################################
import os
import shutil
import io
import codecs
import sys
from BeautifulSoup import BeautifulSoup
import fnmatch

######################################## Start of plugin ###########################################
def Start():
	Log.Debug('Starting %s with a version of %s' %(sTitle, sVersion))
#	print 'Starting %s with a version of %s' %(sTitle, sVersion)

####################################### Movies Plug-In #############################################
class srt2utf8AgentMovies(Agent.Movies):
	name = sTitle + ' (Movies)'
	languages = [Locale.Language.NoLanguage]
	primary_provider = False
	contributes_to = ['com.plexapp.agents.imdb', 'com.plexapp.agents.themoviedb', 'com.plexapp.agents.none']
	# Return a dummy object to satisfy the framework
	def search(self, results, media, lang, manual):
		results.Append(MetadataSearchResult(id='null', score = 100))
    	# Handle the object returned to us, so we can find the directory to look in
	def update(self, metadata, media, lang, force):
		for i in media.items:
			for part in i.parts:
				FindSRT(part)

####################################### TV-Shows Plug-In ###########################################
class srt2utf8AgentTV(Agent.TV_Shows):
	name = sTitle + ' (TV)'
	languages = [Locale.Language.NoLanguage]
	primary_provider = False
	contributes_to = ['com.plexapp.agents.thetvdb', 'com.plexapp.agents.none']

	def search(self, results, media, lang):
		results.Append(MetadataSearchResult(id='null', score = 100))

	# Handle the object returned to us, so we can find the directory to look in
	def update(self, metadata, media, lang, force):
		for s in media.seasons:
			if int(s) < 1900:
				for e in media.seasons[s].episodes:
					for i in media.seasons[s].episodes[e].items:
						for part in i.parts:
							FindSRT(part)

######################################### Find valid sidecars ######################################
def FindSRT(part):
	# Filename of media	
	file = part.file.decode('utf-8')
	# Directory where it's located
	myDir = os.path.dirname(file)
	# Get filename without ext. of the media
	myMedia, myMediaExt = os.path.splitext(os.path.basename(file))
	Log.Debug('Searching directory: %s' %(myDir))
	for root, dirs, files in os.walk(myDir, topdown=False):
		for name in files:
			Log.Debug('File found was: %s' %(name))
			# Get the ext
			sFileName, sFileExtension = os.path.splitext(name)
			lValidList = Prefs['Valid_Ext'].upper().split()
			# IS this a valid subtitle file?
			if (sFileExtension.upper() in lValidList):
				if fnmatch.fnmatch(name, myMedia + '*'):
					Log.Debug('Found a valid subtitle file named %s' %(name))
					sSource = myDir + '/' + name
					GetEnc(sSource)

######################################### Detect the file encoding #################################
def GetEnc(myFile):
	try:
		#Read the subtitle file
		Log.Debug('File to encode is %s' %(myFile))
		f = io.open(myFile, 'rb')
		mySub = f.read()
		soup = BeautifulSoup(mySub)
		soup.contents[0]
		Log.Debug('BeutifulSoap reports encoding as %s' %(soup.originalEncoding))
		if soup.originalEncoding != 'utf-8':
			# Not utf-8, so let's make a backup
			MakeBackup(myFile)
			ConvertFile(myFile, soup.originalEncoding)
		return (soup.originalEncoding == 'utf-8')
	except UnicodeDecodeError:
		Log.Debug('got unicode error with %s' %(myFile))
		return False

######################################## Make the backup, if enabled ###############################
def MakeBackup(file):
	if Prefs['Make_Backup']:	
		sTarget = file + '.' + sTitle
		Log.Debug('Making a backup of %s' %(file))
		shutil.copyfile(file, sTarget)

######################################## Dummy to avoid bad logging ################################
def ValidatePrefs():
	return

########################################## Convert file to utf-8 ###################################
def ConvertFile(myFile, enc):
	Log.Debug('Converting file %s with an encoding of %s' %(myFile, enc))
	with codecs.open(myFile, "r", enc) as sourceFile:
    		with codecs.open(myFile + '.tmpPlex', "w", "utf-8") as targetFile:
        		while True:
            			contents = sourceFile.read()
				if not contents:
					break
				targetFile.write(contents)
	# Remove the origen file
	os.remove(myFile)
	# Name tmp file as the origen
	os.rename(myFile + '.tmpPlex', myFile)
