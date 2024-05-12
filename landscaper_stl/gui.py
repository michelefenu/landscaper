import bpy
import os.path 

from . entity . PDSDetachedLabel import *
from . entity . PDSAttachedLabel import *
from . entity . PDS import *
from . Properties import *

class MakeGUI(bpy.types.Panel) :
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOL_PROPS"
    bl_context = "objectmode"
    bl_label = "Landscaper STL"
    
    def draw(self, context) :
        import_settings = context.scene.import_settings

        # Seleziona il tipo di DTM
        row = self.layout.row()
        row.prop(import_settings, "label_type")

        # Dialog selezione file
        row = self.layout.row()
        row.prop(context.scene, "file_path")

        # Se l'utente ha selezionato un file
        if context.scene.file_path != "" :
            
            try :
                col = self.layout.column()
                split = col.split(align=True)
                split.prop(context.scene, "maximum_latitude", "Northernmost Lat.")
                split.prop(context.scene, "minimum_latitude", "Southernmost Lat.")
                col = self.layout.column()
                split = col.split(align=True)
                split.prop(context.scene, "westernmost_longitude", "Westernmost Long.")
                split.prop(context.scene, "easternmost_longitude", "Easternmost Long.")

                #box = self.layout.box()
                #split = box.split(align=True)
                #split.label(str(MAP_RESOLUTION))
                #split.label("Faces")
            except :
                row = self.layout.row()
                row.label("Si è verificato un errore")


            # Sceglie la proiezione sferica o piana
            row = self.layout.row()
            row.prop(import_settings, "projection_type")

            row = self.layout.row()
            row.prop(context.scene, "z_scaling")

            row = self.layout.row()
            row.operator("mesh.import_dem", text = "Import")
    #end draw
    
