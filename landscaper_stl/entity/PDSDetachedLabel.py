from . PDS import *

class PDSDetachedLabel( PDS ) :

	def __init__( self, file_name, label_name ) :
		self.file_name = file_name
		self.label_name = label_name
		self.label = self.__read_label()

	def get_label( self ) :
		return self.label

	# Legge un file di label testuale e restituisce le informazioni come un dizionario.
	# Vengono eliminati gli spazi, ma non eventuali altri caratteri presenti nel campo value,
	# per cui sarà necessario modificarli manualmente prima di utilizzarli.
	# Se sono presenti informazioni su più righe, verrà inserita solo la prima nel campo value,
	# ma si potrebbe modificare il campo except per aggiungere le altre
	def __read_label( self ) :
		
		# crea il dizionario vuoto
		label = {}

		f = open(self.label_name, 'r')

		# Salva in un dizionario tutte le coppie chiave valore
		for line in f :
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