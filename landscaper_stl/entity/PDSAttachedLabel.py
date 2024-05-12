from . PDS import *

class PDSAttachedLabel( PDS ) :

	def __init__( self, file_name ) :
		self.file_name = file_name
		self.label = self.__read_label()

	def get_label( self ) :
		return self.label

	# Legge un file di label binario e restituisce le informazioni come un dizionario.
	# Vengono eliminati gli spazi, ma non eventuali altri caratteri presenti nel campo value,
	# per cui sarà necessario modificarli manualmente prima di utilizzarli.
	# Se sono presenti informazioni su più righe, verrà inserita solo la prima nel campo value,
	# ma si potrebbe modificare il campo except per aggiungere le altre
	def __read_label( self ) :

		f = open(self.file_name, 'rb')

		# crea il dizionario vuoto
		label = {}

		# Salva in un dizionario tutte le coppie chiave valore
		line = ""
		while line != "END" :
			line = str(f.readline(), 'utf-8').strip()
			if( not line.startswith("/*") ) :
				try :
					token = line.split("=")
					key = token[0].strip()
					value = token[1].strip()
					label[key] = value
				except :
					pass

		f.close()

		return label