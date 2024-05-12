import bpy
import os.path
import math
from math import *
import array
import mathutils
from mathutils import *

class PDS() :

    # Ripulisce i valori presenti nel dizionario leggendo le unità di misura
    # ed impostando le relative variabili di istanza
    def interpret_label( self, raw_label ) :
        
        interpreted_label = {}

        # Nome dell'oggetto
        try :
            interpreted_label['TARGET_NAME'] = raw_label['TARGET_NAME']
        except :
            interpreted_label['TARGET_NAME'] = ""

        # TYPE in {BODY-FIXED ROTATING}
        try :
            interpreted_label['COORDINATE_SYSTEM_TYPE'] = raw_label['COORDINATE_SYSTEM_TYPE']
        except :
            interpreted_label['COORDINATE_SYSTEM_TYPE'] = ""

        # NAME in {MEAN EARTH/POLAR AXIS OF DE421, PLANETOCENTRIC}
        try :
            interpreted_label['COORDINATE_SYSTEM_NAME'] = raw_label['COORDINATE_SYSTEM_NAME']
        except :
            interpreted_label['COORDINATE_SYSTEM_NAME'] = ""

        interpreted_label['MAP_PROJECTION_TYPE'] = raw_label['MAP_PROJECTION_TYPE']
        try :
            interpreted_label['SCALING_FACTOR'] = float(raw_label['SCALING_FACTOR'])
        except :
            interpreted_label['SCALING_FACTOR'] = 1.0

        # Importa i dati necessari dal file di label
        interpreted_label['MAP_RESOLUTION'] = float(raw_label['MAP_RESOLUTION'].split("<")[0].strip())  
        interpreted_label['LINE_SAMPLES'] = int(raw_label['LINE_SAMPLES'])                                                                                                                        
        interpreted_label['LINES'] = int(raw_label['LINES'])
        interpreted_label['SAMPLE_BITS'] = int(raw_label['SAMPLE_BITS'])

        # Aggiungo il valore del pixel centrale
        # La latitudine minore sarà 0 + la risoluzione della mappa
        interpreted_label['EASTERNMOST_LONGITUDE'] = float(raw_label['EASTERNMOST_LONGITUDE'].split("<")[0].strip()) - 1 / interpreted_label['MAP_RESOLUTION'] 
        interpreted_label['WESTERNMOST_LONGITUDE'] = float(raw_label['WESTERNMOST_LONGITUDE'].split("<")[0].strip()) + 1 / interpreted_label['MAP_RESOLUTION'] 
        interpreted_label['MAXIMUM_LATITUDE'] = float(raw_label['MAXIMUM_LATITUDE'].split("<")[0].strip()) - 1 / interpreted_label['MAP_RESOLUTION'] 
        interpreted_label['MINIMUM_LATITUDE'] = float(raw_label['MINIMUM_LATITUDE'].split("<")[0].strip()) + 1 / interpreted_label['MAP_RESOLUTION'] 

        # Dati definiti dall'utente
        self.SCALE_FACTOR                   = 40.0
        self.LAT_SKIP                       = 1     # Legge un punto ogni x
        self.LON_SKIP                       = 1


        # Imposta l'unità di misura usata dal dataset
        try :                  
            if raw_label['UNIT'] == "KM" :
                interpreted_label['UNIT'] = 1
            else :
                interpreted_label['UNIT'] = 1000
        except :
            # Di default assumiamo i metri
            interpreted_label['UNIT'] = 1000

        interpreted_label['A_AXIS_RADIUS'] = float(raw_label['A_AXIS_RADIUS'].split("<")[0].strip())
        interpreted_label['B_AXIS_RADIUS'] = float(raw_label['B_AXIS_RADIUS'].split("<")[0].strip())
        interpreted_label['C_AXIS_RADIUS'] = float(raw_label['C_AXIS_RADIUS'].split("<")[0].strip())

        # MSB O LSB 
        interpreted_label['SAMPLE_TYPE'] = raw_label['SAMPLE_TYPE']

        # Calcola il raggio medio
        interpreted_label['RADIUS'] = (
            interpreted_label['A_AXIS_RADIUS'] 
            + interpreted_label['B_AXIS_RADIUS'] 
            + interpreted_label['C_AXIS_RADIUS'] ) / 3 * interpreted_label['UNIT']

        return interpreted_label


    def read_data_sphere( self ) :       

        label = self.interpret_label( self.label )

        maximum_latitude = self.RealLat(bpy.context.scene.maximum_latitude, label)
        minimum_latitude = self.RealLat(bpy.context.scene.minimum_latitude, label)
        easternmost_longitude = self.RealLong(bpy.context.scene.easternmost_longitude, label)
        westernmost_longitude = self.RealLong(bpy.context.scene.westernmost_longitude, label)


        f = open(self.file_name, 'rb')

        # Deve skippare i primi n byte se l'etichetta è in testa al file
        # controlla se l'immagine fa riferimento ad un file img separato
        if not "IMG" in self.label['^IMAGE'] :
            skip = int( self.label['^IMAGE'].split("<")[0].strip() ) - 1
            b = f.read( skip )

        # A seconda del formato del file devo leggere gli elementi in maniera opportuna
        bytes_to_read = int(label['LINES'] * label['LINE_SAMPLES'] * (label['SAMPLE_BITS'] / 8))
        s = f.read(bytes_to_read) 

        if label['SAMPLE_TYPE'] == "LSB_INTEGER" :
            altimetry = array.array("h", s) # Creo un array di signed shorts
        elif label['SAMPLE_TYPE'] == "MSB_INTEGER" :
            altimetry = array.array("h", s) # Creo un array di signed shorts
            altimetry.byteswap()
        elif label['SAMPLE_TYPE'] == "4BYTE_FLOAT" or "PC_REAL" :
            altimetry = array.array("f", s) # Creo un array di signed shorts
        
        f.close()

        verts = [] 
        faces = []
        
        step = radians(1 / label['MAP_RESOLUTION'])       

        # Indice del primo punto da leggere
        point = (self.LatToLine(maximum_latitude, label) - 1) * label['LINE_SAMPLES']
        # numero di elementi da saltare all'inizio di ogni riga
        start_skip = self.LongToPoint(westernmost_longitude, label) - 1
        # points
        read_points = self.LongToPoint(easternmost_longitude, label) - self.LongToPoint(westernmost_longitude, label) + 1
        # numero di elementi da saltare alla fine di ogni riga
        end_skip = label['LINE_SAMPLES'] - start_skip - read_points
        
        if label['MAP_RESOLUTION'] ==  16 :
                end_skip += 1

        lat = radians(maximum_latitude)
        edgeloop_prev = []

        if label['EASTERNMOST_LONGITUDE'] == easternmost_longitude and label['WESTERNMOST_LONGITUDE'] == westernmost_longitude :
            close_faces = True
        else :
            close_faces =  False
            
        while(lat >= radians(minimum_latitude)) :
            
            # Calcola la co latitudine per disegnare la sfera
            edgeloop_cur = []
            co_lat = lat*(-1) + radians(90)

            # salta i primi n punti di longitudine
            point = point + start_skip

            lon = radians(westernmost_longitude)

            while(lon <= radians(easternmost_longitude)) :
                try :
                    r = ((label['RADIUS'] + altimetry[point])/label['UNIT']/label['SCALING_FACTOR'] ) / self.SCALE_FACTOR 
                except :
                    r = label['RADIUS'] / self.SCALE_FACTOR 
                x = r * sin(co_lat) * cos(lon)
                y = r * sin(co_lat) * sin(lon)
                z = r * cos(co_lat)
                edgeloop_cur.append(len(verts))
                verts.append((float(x), float(y), float(z)))
                point += 1
                lon += step
            #end for

            # Se non siamo al primo giro
            if len(edgeloop_prev) > 0 :
                faces_row = self.createFaces(edgeloop_prev, edgeloop_cur, True)
                faces.extend(faces_row)

            edgeloop_prev = edgeloop_cur
            lat -= step
            # Salta gli ultimi n punti della riga
            
            point = point + end_skip

        #end for
        
        del altimetry

        return verts, faces


    def read_data_plane( self ) :       

        label = self.interpret_label( self.label )

        maximum_latitude = self.RealLat(bpy.context.scene.maximum_latitude, label)
        minimum_latitude = self.RealLat(bpy.context.scene.minimum_latitude, label)
        easternmost_longitude = self.RealLong(bpy.context.scene.easternmost_longitude, label)
        westernmost_longitude = self.RealLong(bpy.context.scene.westernmost_longitude, label)


        f = open(self.file_name, 'rb')

        # Deve skippare i primi n byte se l'etichetta è in testa al file
        # controlla se l'immagine fa riferimento ad un file img separato
        if not "IMG" in self.label['^IMAGE'] :
            skip = int( self.label['^IMAGE'].split("<")[0].strip() ) - 1
            b = f.read( skip )

        # A seconda del formato del file devo leggere gli elementi in maniera opportuna
        bytes_to_read = int(label['LINES'] * label['LINE_SAMPLES'] * (label['SAMPLE_BITS'] / 8))
        s = f.read(bytes_to_read) 

        if label['SAMPLE_TYPE'] == "LSB_INTEGER" :
            altimetry = array.array("h", s) # Creo un array di signed shorts
        elif label['SAMPLE_TYPE'] == "MSB_INTEGER" :
            altimetry = array.array("h", s) # Creo un array di signed shorts
            altimetry.byteswap()
        elif label['SAMPLE_TYPE'] == "4BYTE_FLOAT" or "PC_REAL" :
            altimetry = array.array("f", s) # Creo un array di signed shorts
        
        f.close()

        verts = [] 
        faces = []
        
        step = radians(1 / label['MAP_RESOLUTION'])       

        # Indice del primo punto da leggere
        point = (self.LatToLine(maximum_latitude, label) - 1) * label['LINE_SAMPLES']
        # numero di elementi da saltare all'inizio di ogni riga
        start_skip = self.LongToPoint(westernmost_longitude, label) - 1
        # points
        read_points = self.LongToPoint(easternmost_longitude, label) - self.LongToPoint(westernmost_longitude, label) + 1
        # numero di elementi da saltare alla fine di ogni riga
        end_skip = label['LINE_SAMPLES'] - start_skip - read_points
        
        if label['MAP_RESOLUTION'] ==  16 :
                end_skip += 1

        lat = radians(maximum_latitude)
        edgeloop_prev = []
        while(lat >= radians(minimum_latitude)) :
            
            # Calcola la co latitudine per disegnare la sfera
            edgeloop_cur = []
            co_lat = lat*(-1) + radians(90)

            # salta i primi n punti di longitudine
            point = point + start_skip

            lon = radians(westernmost_longitude)

            while(lon <= radians(easternmost_longitude)) :
                try :
                    r = ((altimetry[point])/label['UNIT']/label['SCALING_FACTOR'] ) / self.SCALE_FACTOR 
                except :
                    r = label['RADIUS'] / self.SCALE_FACTOR 
                x = (degrees(lon) - westernmost_longitude) 
                y = (degrees(lat) - minimum_latitude)
                z = r
                edgeloop_cur.append(len(verts))
                verts.append((float(x), float(y), float(z)))
                point += 1
                lon += step
            #end for

            # Se non siamo al primo giro
            if len(edgeloop_prev) > 0 :
                faces_row = self.createFaces(edgeloop_prev, edgeloop_cur)
                faces.extend(faces_row)

            edgeloop_prev = edgeloop_cur
            lat -= step
            # Salta gli ultimi n punti della riga
            
            point = point + end_skip

        #end for
        
        del altimetry

        return verts, faces

    # end read_data_plane

    def read_data_printable_model( self ) :       

        label = self.interpret_label( self.label )

        maximum_latitude = self.RealLat(bpy.context.scene.maximum_latitude, label)
        minimum_latitude = self.RealLat(bpy.context.scene.minimum_latitude, label)
        easternmost_longitude = self.RealLong(bpy.context.scene.easternmost_longitude, label)
        westernmost_longitude = self.RealLong(bpy.context.scene.westernmost_longitude, label)


        f = open(self.file_name, 'rb')

        # Deve skippare i primi n byte se l'etichetta è in testa al file
        # controlla se l'immagine fa riferimento ad un file img separato
        if not "IMG" in self.label['^IMAGE'] :
            skip = int( self.label['^IMAGE'].split("<")[0].strip() ) - 1
            b = f.read( skip )

        # A seconda del formato del file devo leggere gli elementi in maniera opportuna
        bytes_to_read = int(label['LINES'] * label['LINE_SAMPLES'] * (label['SAMPLE_BITS'] / 8))
        s = f.read(bytes_to_read) 

        if label['SAMPLE_TYPE'] == "LSB_INTEGER" :
            altimetry = array.array("h", s) # Creo un array di signed shorts
        elif label['SAMPLE_TYPE'] == "MSB_INTEGER" :
            altimetry = array.array("h", s) # Creo un array di signed shorts
            altimetry.byteswap()
        elif label['SAMPLE_TYPE'] == "4BYTE_FLOAT" or "PC_REAL" :
            altimetry = array.array("f", s) # Creo un array di signed shorts
        
        f.close()

        verts = [] 
        faces = []
        
        step = radians(1 / label['MAP_RESOLUTION'])       

        # Indice del primo punto da leggere
        point = (self.LatToLine(maximum_latitude, label) - 1) * label['LINE_SAMPLES']
        # numero di elementi da saltare all'inizio di ogni riga
        start_skip = self.LongToPoint(westernmost_longitude, label) - 1
        # points
        read_points = self.LongToPoint(easternmost_longitude, label) - self.LongToPoint(westernmost_longitude, label) + 1
        # numero di elementi da saltare alla fine di ogni riga
        end_skip = label['LINE_SAMPLES'] - start_skip - read_points
        
        if label['MAP_RESOLUTION'] ==  16 :
                end_skip += 1

        lat = radians(maximum_latitude)
        edgeloop_prev = []
        while(lat >= radians(minimum_latitude)) :
            
            # Calcola la co latitudine per disegnare la sfera
            edgeloop_cur = []
            co_lat = lat*(-1) + radians(90)

            # salta i primi n punti di longitudine
            point = point + start_skip

            lon = radians(westernmost_longitude)

            while(lon <= radians(easternmost_longitude)) :
                try :
                    r = ((altimetry[point])/label['UNIT']/label['SCALING_FACTOR'] ) / self.SCALE_FACTOR 
                except :
                    r = label['RADIUS'] / self.SCALE_FACTOR 
                x = (degrees(lon) - westernmost_longitude) 
                y = (degrees(lat) - minimum_latitude)
                # Scala z in base alle preferenze dell'utente
                z = r * bpy.context.scene.z_scaling
                edgeloop_cur.append(len(verts))
                verts.append((float(x), float(y), float(z)))
                point += 1
                lon += step
            #end for

            # Se non siamo al primo giro
            if len(edgeloop_prev) > 0 :
                faces_row = self.createFaces(edgeloop_prev, edgeloop_cur)
                faces.extend(faces_row)

            edgeloop_prev = edgeloop_cur
            lat -= step
            # Salta gli ultimi n punti della riga
            
            point = point + end_skip

        #end for
        
        del altimetry

        return verts, faces

        # end read data printable model

    def get_sphere( self ) :
        return self.read_data_sphere()

    def get_plane( self ) :
        return self.read_data_plane()

    def get_printable_model( self ) :
        return self.read_data_printable_model()


    #Utility Function ********************************************************
    #
    #Input: Latitude Output: Number of the line (1 to n)
    def LatToLine(self, Latitude, label):
        tmpLines = round((label['MAXIMUM_LATITUDE'] - Latitude) * label['MAP_RESOLUTION'] + 1.0)
        if tmpLines > label['LINES']:
            tmpLines = label['LINES']
        return tmpLines


    #Input: Number of the line (1 to n) Output: Latitude
    def LineToLat(self, Line, label):
        if label['MAP_RESOLUTION'] == 0:
            return 0
        else:
            return float(label['MAXIMUM_LATITUDE'] - (Line -1) / label['MAP_RESOLUTION'])


    #Input: Longitude Output: Number of the point (1 to n)
    def LongToPoint(self, Longitude, label):
        tmpPoints = round((Longitude - label['WESTERNMOST_LONGITUDE']) * label['MAP_RESOLUTION'] + 1.0)
        if tmpPoints > label['LINE_SAMPLES']:
            tmpPoints = label['LINE_SAMPLES']
        return tmpPoints


    #Input: Number of the Point (1 to n) Output: Longitude
    def PointToLong(self, Point, label):
        if label['MAP_RESOLUTION'] == 0:
            return 0
        else:
            return float(label['WESTERNMOST_LONGITUDE'] + (Point-1) / label['MAP_RESOLUTION'])


    #Input: Latitude Output: Neareast real Latitude on grid
    def RealLat(self, Latitude, label):
        return float(self.LineToLat(self.LatToLine(Latitude, label), label))


    #Input: Longitude Output: Neareast real Longitude on grid
    def RealLong(self, Longitude, label):
        return float(self.PointToLong(self.LongToPoint(Longitude, label), label))

    #**************************************************************************
    # A very simple "bridge" tool.
    # Connects two equally long vertex rows with faces.
    # Returns a list of the new faces (list of  lists)
    #
    # vertIdx1 ... First vertex list (list of vertex indices).
    # vertIdx2 ... Second vertex list (list of vertex indices).
    # closed ... Creates a loop (first & last are closed).
    # flipped ... Invert the normal of the face(s).
    #
    # Note: You can set vertIdx1 to a single vertex index to create
    #    a fan/star of faces.
    # Note: If both vertex idx list are the same length they have
    #    to have at least 2 vertices.
    def createFaces(self, vertIdx1, vertIdx2, closed=False, flipped=False):
        faces = []

        if not vertIdx1 or not vertIdx2:
            return None

        if len(vertIdx1) < 2 and len(vertIdx2) < 2:
            return None

        fan = False
        if (len(vertIdx1) != len(vertIdx2)):
            if (len(vertIdx1) == 1 and len(vertIdx2) > 1):
                fan = True
            else:
                return None

        total = len(vertIdx2)

        if closed:
            # Bridge the start with the end.
            if flipped:
                face = [
                    vertIdx1[0],
                    vertIdx2[0],
                    vertIdx2[total - 1]]
                if not fan:
                    face.append(vertIdx1[total - 1])
                faces.append(face)

            else:
                face = [vertIdx2[0], vertIdx1[0]]
                if not fan:
                    face.append(vertIdx1[total - 1])
                face.append(vertIdx2[total - 1])
                faces.append(face)

        # Bridge the rest of the faces.
        for num in range(total - 1):
            if flipped:
                if fan:
                    face = [vertIdx2[num], vertIdx1[0], vertIdx2[num + 1]]
                else:
                    face = [vertIdx2[num], vertIdx1[num],
                        vertIdx1[num + 1], vertIdx2[num + 1]]
                faces.append(face)
            else:
                if fan:
                    face = [vertIdx1[0], vertIdx2[num], vertIdx2[num + 1]]
                else:
                    face = [vertIdx1[num], vertIdx2[num],
                        vertIdx2[num + 1], vertIdx1[num + 1]]
                faces.append(face)

        return faces
