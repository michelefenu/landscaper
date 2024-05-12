import bpy

# Impostazioni per l'importatore di terrain
class ImportSettings(bpy.types.PropertyGroup) :

    # Tipo del file da importare 
    label_type = bpy.props.EnumProperty(
        name="Label type",
        description="Detached if you have the label in a separate file, Attached otherwise",
        items=(
            ('PDS_ATTACHED', "Attached", ""),
            ('PDS_DETACHED', "Detached", "Label (.lbl) and data (.img) must be in the same folder"),
            ),
        default='PDS_ATTACHED'
        )

    # Proietta i punti su una sfera o su un piano
    projection_type = bpy.props.EnumProperty(
        name="Shape",
        description="Import the points on a sphere or a plane",
        items=(
            ('SPHERE', "Sphere", "Suitable for large areas and for all the planet surface"),
            ('PLANE', "Plane", "Suitable for small areas"),
            ('PRINTABLE', "Printable model", "Creates a model 3D print compliant")
            ),
        default='SPHERE'
        )