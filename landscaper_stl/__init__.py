# BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Landscaper STL",
    "author": "Michele Fenu",
    "version": (0, 0, 1),
    "blender": (2, 6, 5),
    "api": 53207,
    "location": "3D window > Tool Shelf",
    "description": "Import PDS DEM Files and makes 3D printing ready models",
    "warning": "",
    "wiki_url": "",
        "tracker_url": "",
    "category": "3D View"}

import bpy

from . Properties import *
from . ImportDEM import *
from . gui import *

# registering the script
def register() :
    bpy.utils.register_class(MakePlanet)
    bpy.utils.register_class(MakeGUI)

    bpy.utils.register_class(ImportSettings)
    bpy.types.Scene.import_settings = (
        bpy.props.PointerProperty(type=ImportSettings,
            name="Terrain",
            description="Terrain importer Settings"))
        # Percorso del file img



    bpy.types.Scene.file_path = bpy.props.StringProperty(
        name = "", 
        description = "Select your IMG file", 
        subtype = "FILE_PATH", 
        default = "",
        update=update_properties 
        )

    bpy.types.Scene.z_scaling = bpy.props.FloatProperty(
            description = "Z scaling", 
            min = float( 1.0 ), 
            max = float( 5.0 ), 
            precision = 3,
            default = 1.0 )

#end register

def unregister() :
    bpy.utils.unregister_class(MakePlanet)
    bpy.utils.unregister_class(MakeGUI)

    bpy.utils.unregister_class(ImportSettings)
#end unregister

# Properties per l'importazione
def update_properties(self, context) :

    import_settings = context.scene.import_settings

    if context.scene.file_path != "" :
        try :
            if import_settings.label_type == 'PDS_DETACHED' :
                label_name = os.path.splitext(context.scene.file_path)[0]+".lbl"
                dtm = PDSDetachedLabel( context.scene.file_path, label_name )                                      
            else :
                dtm = PDSAttachedLabel( context.scene.file_path )
                
            label = dtm.get_label()
            label_clean = dtm.interpret_label( label )
            
        except :
            pass

        # Estremi delle coordinate per l'importazione
        bpy.types.Scene.maximum_latitude = bpy.props.FloatProperty(
            description = "From Latitude", 
            min = float( label_clean['MINIMUM_LATITUDE'] ), 
            max = float( label_clean['MAXIMUM_LATITUDE'] ), 
            precision = 3, 
            default = 90.0 )
        bpy.types.Scene.minimum_latitude = bpy.props.FloatProperty(
            description = "To Latitude", 
            min = float( label_clean['MINIMUM_LATITUDE'] ), 
            max = float( label_clean['MAXIMUM_LATITUDE'] ), 
            precision = 3,
            default = -90.0 )
        bpy.types.Scene.westernmost_longitude = bpy.props.FloatProperty(
            description = "From Longitude", 
            min = float( label_clean['WESTERNMOST_LONGITUDE'] ), 
            max = float( label_clean['EASTERNMOST_LONGITUDE'] ), 
            precision = 3,
            default = -180.0 )
        bpy.types.Scene.easternmost_longitude = bpy.props.FloatProperty(
            description = "To Longitude", 
            min = float( label_clean['WESTERNMOST_LONGITUDE'] ), 
            max = float( label_clean['EASTERNMOST_LONGITUDE'] ), 
            precision = 3,
            default = 360.0 )
        

        #bpy.types.Scene.scale = bpy.props.IntProperty(description="Scale", min=1, max=100, default=1)
#end import properties
