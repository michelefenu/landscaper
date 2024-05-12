import bpy
import os.path
import math
from math import *
import array
import mathutils
from mathutils import *

from . entity . PDSDetachedLabel import *
from . entity . PDSAttachedLabel import *

from . Label import *
    
class MakePlanet(bpy.types.Operator):
    bl_idname = "mesh.import_dem"
    bl_label = "Landscaper"
   
    def action_common(self, context) :

        # Proprieta del terrain
        import_settings = context.scene.import_settings

        # turn off undo
        undo = bpy.context.user_preferences.edit.use_global_undo
        bpy.context.user_preferences.edit.use_global_undo = False

        # Istanzia la label 
        label = Label()

        label_name = os.path.splitext(context.scene.file_path)[0]+".lbl"
        if import_settings.label_type == 'PDS_DETACHED' :
            label_name = os.path.splitext(context.scene.file_path)[0]+".lbl"
            label.read_detached_label( label_name )
        else :
            label.read_attached_label( context.scene.file_path )

        
       
        # lancia un'eccezione se non è stato selezionato un file
        if context.scene.file_path == "" :
            raise NameError("Nessun file selezionato")

        label_name = os.path.splitext(context.scene.file_path)[0]+".lbl"
        if import_settings.label_type == 'PDS_DETACHED' :
            label_name = os.path.splitext(context.scene.file_path)[0]+".lbl"
            dtm = PDSDetachedLabel( context.scene.file_path, label_name )                                      
        else :
            dtm = PDSAttachedLabel( context.scene.file_path )
        
        if import_settings.projection_type == "SPHERE" :
            verts, faces = dtm.get_sphere()
        elif  import_settings.projection_type == "PLANE":
            verts, faces = dtm.get_plane()
        elif  import_settings.projection_type == "PRINTABLE":
            verts, faces = dtm.get_printable_model()

        # crea una nuova mesh
        mesh = bpy.data.meshes.new(dtm.get_label()['TARGET_NAME'])
        # importa vertici, lati e facce nella mesh appena creata
        mesh.from_pydata(verts, [], faces)
        
        # Update sfera
        mesh.update()
        # crea l'oggetto Sfera associando la mesh appena creata
        object = bpy.data.objects.new(dtm.get_label()['TARGET_NAME'], mesh)

        # aggiunge l'oggetto alla scena
        bpy.context.scene.objects.link(object)
        # seleziona questo oggetto per modifiche future
        bpy.ops.object.select_all(action = "DESELECT")
        object.select = True
        context.scene.objects.active = object

        # Crea la base per l'oggetto stampabile
        if  import_settings.projection_type == "PRINTABLE":
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, -1), "constraint_axis":(False, False, True), "constraint_orientation":'NORMAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
            bpy.ops.transform.resize(value=(1, 1, 0), constraint_axis=(False, False, True), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
            bpy.ops.object.editmode_toggle()

        # Sposta l'origine nel centro geometrico dell'oggetto
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

        # Metterlo opzionale
        #bpy.ops.object.mode_set(mode='EDIT')
        #bpy.ops.mesh.normals_make_consistent(inside=False)
        #bpy.ops.object.mode_set(mode='OBJECT')
        # sphere, remove doubles
        #if import_settings.projection_type =="SPHERE":
        #   bpy.ops.object.mode_set(mode='EDIT')
        #   bpy.ops.mesh.remove_doubles(threshold=0.0001)
        #   bpy.ops.object.mode_set(mode='OBJECT')  

        # restore pre operator undo state
        bpy.context.user_preferences.edit.use_global_undo = undo


    # end action_common
    
    def execute(self, context) :
        self.action_common(context)
        return {"FINISHED"}
    #end execute
 
    def invoke(self, context, event) :
        self.action_common(context)
        return {"FINISHED"}
    #end invoke

#end MakePlanet
