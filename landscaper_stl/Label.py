# Gli elementi della label sono salvati in un dizionario come coppie
# chiave-valore
# Bisognerebbe scrivere il parser ricorsivo ma per il momento ci accontentiamo
class Label() :
	
	# crea il dizionario vuoto
	label = {}

	#TO-DO Legge il nome del file, controlla che tutto sia a posto e chiama la funzione
	# read_att o detach label per parsificarlo

	# A questo punto la label è stata letta, bisogna interpretare correttamente i dati
	# eliminare gli spazi ecc.. ecc.. quindi chiama funzione interpret label


	# Legge un file di label testuale e restituisce le informazioni come un dizionario.
	# Vengono eliminati gli spazi, ma non eventuali altri caratteri presenti nel campo value,
	# per cui sarà necessario modificarli manualmente prima di utilizzarli.
	# Se sono presenti informazioni su più righe, verrà inserita solo la prima nel campo value,
	# ma si potrebbe modificare il campo except per aggiungere le altre
	def read_detached_label( self, file_name ) :

		# Inizializza il dizionario
		label = {}

		f = open(file_name, 'r')

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

		self.__interpret_label()


	# Legge un file di label binario e restituisce le informazioni come un dizionario.
	# Vengono eliminati gli spazi, ma non eventuali altri caratteri presenti nel campo value,
	# per cui sarà necessario modificarli manualmente prima di utilizzarli.
	# Se sono presenti informazioni su più righe, verrà inserita solo la prima nel campo value,
	# ma si potrebbe modificare il campo except per aggiungere le altre
	def read_attached_label( self, file_name ) :

		# Inizializza il dizionario
		label = {}

		f = open(file_name, 'rb')

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

		self.__interpret_label()

	def __interpret_label( self ) :
		pass
