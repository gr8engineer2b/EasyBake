import bpy

from mathutils import (Vector, Euler)
# Class Types
from bpy.types import (Operator, Menu, Scene, Panel, Object, PropertyGroup)
# Variable (Property) Types
from bpy.props import (IntProperty, BoolProperty, FloatProperty,
                       StringProperty, CollectionProperty, EnumProperty)
# Necessary for basic blender addon initialization
from bpy.utils import (register_class, unregister_class)


if "bpy" in locals():  # Load addon scripts
    import importlib
    importlib.reload(sound_bake)
else:
    from . import sound_bake


bl_info = {
    'name': 'Easy Bake',
    'author': 'gr8engineer2b',
    'version': (2, 0, 0),
    'blender': (3, 0, 0),
    'location': 'Tool > Easy Bake',
    'description': "Easy Sound Baking",
    'category': 'Tool',
}

# Property setup


def enum_populate(self, context):
    object = context.object
    nameins = ''
    items = []

    if object.animation_data:
        if object.animation_data.action:
            for x in object.animation_data.action.fcurves:
                if x.array_index == 0:
                    if "location" not in x.data_path or \
                        "rotation" not in x.data_path or \
                            "scale" not in x.data_path:
                        nameins = ""
                elif x.array_index == 1:
                    nameins = " Y"
                elif x.array_index == 2:
                    nameins = " Z"
                else:
                    nameins = " X"

                items.append((x.data_path+" "+str(x.array_index), x.data_path +
                              "{0}".format(nameins), x.data_path +
                              " index "+str(x.array_index)))
    # if [x.material.node_tree.animation_data for x in object.material_slots]:
    #     if None not in [x.material.node_tree.animation_data
    #                     for x in object.material_slots]:
    #         pass  # TODO: Write material key Handling code

    return items


# TODO: probably not clean, doing this just in case to prevent loading order
# from creating errors
def propinit():

    # TODO: unused variable? remove?
    Scene.stepchoice = \
        IntProperty(name="stepchoice", default=64, max=1024, min=2, step=2)

    Scene.barchoice = \
        IntProperty(name="barchoice", default=64, max=1024, min=2, step=2)
    Scene.barwidth = \
        IntProperty(name="barwidth", default=16, max=1024, min=1, step=1)
    Scene.barheight = \
        IntProperty(name="barheight", default=8, max=1024, min=1, step=1)
    Scene.bakefromzero = \
        BoolProperty(name="bakefromzero", default=1)
    Scene.halfheight = \
        BoolProperty(name="halfheight", default=1)
    Scene.barwidthmod = \
        FloatProperty(
            name="barwidthmod", default=1.0, max=1.0, min=0.01, step=0.01)
    Scene.bakeattack = \
        FloatProperty(name="bakeattack", default=0.01, min=0.01, step=0.01)
    Scene.bakerelease = \
        FloatProperty(name="bakerelease", default=0.01, min=0.01, step=0.01)

    Object.dataoptions = EnumProperty(
        items=enum_populate,
    )

    Object.frequencystart = \
        IntProperty(name="frequencystart", default=20, min=0, step=100)
    Object.frequencyend = \
        IntProperty(name="frequencyend", default=20000, min=0, step=100)
    Object.bakeattack = \
        FloatProperty(name="bakeattack", default=0.01, min=0.01, step=0.01)
    Object.bakerelease = \
        FloatProperty(name="bakerelease", default=0.01, min=0.01, step=0.01)
    Object.maximumfrequency = \
        IntProperty(name="maximumfrequency", default=16000, min=1, step=1)
    Object.minimumfrequency = \
        IntProperty(name="minimumfrequency", default=20, min=20, step=1)

    Object.frequencyinfluence = \
        IntProperty(name="frequencyinfluence", default=1)
    Object.frequencychoice = \
        StringProperty(name="frequencychoice", default="")

    Scene.frequencyoptions = CollectionProperty(type=FreqCollection)


class FreqCollection(PropertyGroup):
    objname: StringProperty(name="objname")
    range: StringProperty(name="range")

# End Property setup


# Cleanup function for old/uneccessary data
# TODO:  move to seperate script once init becomes cluttered

def removechildren(object, namecheck=""):
    removed = False
    if object.children:
        for child in object.children:
            if namecheck:
                if namecheck in child.name:
                    bpy.data.objects.remove(child)
                    removed = True
            else:
                bpy.data.objects.remove(child)
                removed = True
    return removed

# Will not remove blender objects unless specified


def cleanbars(cleanobjects=False):
    if cleanobjects is True:
        for x in bpy.data.objects:
            objname = x.name
            if not x.parent:
                if "SoundBar" in objname:
                    removechildren(x, "DataEmpty")
                    bpy.data.objects.remove(x)
                elif "DataEmpty" in objname:  # elif technically uneeded
                    bpy.data.objects.remove(x)


# Classes


class SoundBakeUI(Panel):
    # Use this as a tooltip for menu items and buttons.
    """
    Easy (Sound) Bake
    """
    # Unique identifier for buttons and menu items to reference.
    bl_idname = 'TOOL_PT_soundbakeui'
    # Display name in the interface.
    bl_label = 'Easy Bake'
    bl_region_type = 'UI'
    bl_space_type = 'VIEW_3D'
    bl_context = 'objectmode'

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        # converted from old column to new on-screen ui
        col = layout.column()
        row = col.row()
        row.label(text='Bars: ')
        row.prop(scene, 'barchoice', text='Number of Bars')
        row = col.row()
        row.label(text='Height: ')
        row.prop(scene, 'barheight', text='Overall Height in Units')
        row = col.row()
        row.label(text='Width: ')
        row.prop(scene, 'barwidth', text='Overall Width in Units')
        row = col.row()
        row.prop(scene, 'barwidthmod', text='Width:')
        row.operator('tool.bars_create', text='Create Bars')

        row = col.row()
        row.label(text='Camera: ')
        row.operator('tool.camera_create', text='Create/Reposition Camera')

        row = col.row()
        row.prop(scene, 'bakefromzero', text='Bake from Frame 0')
        row.prop(scene, 'halfheight', text='Center Origin (Double Sided)')


class FrequencyMenu(Menu):
    # Unique identifier for buttons and menu items to reference.
    bl_idname = 'OBJECT_MT_frequencymenu'
    # Display name in the interface.
    bl_label = 'Frequency Menu'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        if scene.frequencyoptions:
            for x in context.scene.frequencyoptions:
                layout.operator('object.frequency_assign', text=x.range)\
                    .freqobjname = x.objname
        else:
            layout.label(text='Bake a Frequency for options')


class BakeProps(Panel):
    # Unique identifier for buttons and menu items to reference.
    bl_idname = 'OBJECT_PT_bakepropsui'
    # Display name in the interface.
    bl_label = 'Bake Properties'
    bl_description = 'Baked frequency to use for animation'
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_context = "object"

    def draw(self, context):
        object = context.object
        layout = self.layout
        scene = context.scene

        col = layout.column()

        # DOCUMENTATION: flimsy nameing scheme implementation could easily be
        # renamed and likely to happen
        if "Bars" not in object.name:
            row = col.row()
            row.label(text='Path: ')
            row.prop(object, 'dataoptions', text='')
            row = col.box()
            row.label(text='Copy Frequency: ')
            row.menu('OBJECT_MT_frequencymenu', text="Select")
            row = col.row()
            row.prop(object, 'frequencyinfluence', text="Influence")
            row = col.row()
            row.label(text='Custom Range: ')
            row = col.row()
            row.prop(object, 'frequencystart', text="Frequency Min")
            row.prop(object, 'frequencyend', text="Frequency Max")
            row = col.row()
            row.prop(object, 'bakeattack', text="Attack")
            row.prop(object, 'bakerelease', text="Release")

        row = col.row()
        row.operator('tool.easy_bake', text='Bake').objectname = object.name

        if "Bars" in object.name:
            row = col.row()
            row.prop(object, 'minimumfrequency', text='Min Frequency')
            row.prop(object, 'maximumfrequency', text='Max Frequency')

        row = col.row()
        row.prop(scene, 'bakefromzero', text='Bake from Frame 0')


class MakeCamera(Operator):
    bl_idname = 'tool.camera_create'
    bl_label = 'Create Camera'
    bl_description = "Creates or readjusts camera for "\
        "easy rendering of a single bar visualizer"
    bl_options = {'REGISTER', 'UNDO'}

    # execute() is called when running the operator.
    def execute(self, context):
        collection = bpy.context.collection
        try:
            # xyz
            bpy.data.objects['Camera'].location = Vector([24, 0, 0])
            # values copied
            bpy.data.objects['Camera'].rotation_euler =\
                Euler((1.5707963705062866,
                       0.0,
                       1.5707963705062866), ('XYZ'))
        # If KeyError, try camera creation
        except KeyError as e:
            print('Creating camera: {0}'.format(e))
            try:
                camera = bpy.data.cameras.new()
                object = bpy.data.objects.new("Camera", camera)
                object.location = (24, 0, 0)
                object.rotation_euler = Euler((1.5707963705062866,
                                               0.0,
                                               1.5707963705062866))
                bpy.data.collections[collection].objects.link(object)
            except Exception as e:
                print('Camera creation Failed, {0}'.format(e))

        return {'FINISHED'}


class MakeBars(Operator):
    bl_idname = 'tool.bars_create'
    bl_label = 'Easy Bars'
    bl_description = "Construct bar mesh"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    def execute(self, context):
        scene = context.scene
        barchoice = scene.barchoice
        widthmod = scene.barwidthmod
        halfheight = scene.halfheight
        arealength = scene.barwidth
        movedistance = arealength/barchoice
        width = (arealength/barchoice)*widthmod
        height = scene.barheight

        if not barchoice == 0:

            bpy.ops.object.select_all(action='DESELECT')

            verts = [(0.0, -(width/2), 0.0),
                     (0.0, width/2, 0.0),
                     (0.0, width/2, height),
                     (0.0, -(width/2), height)]
            faces = [(0, 1, 2, 3)]

            material = bpy.data.materials.new('Bars.000')
            collection = bpy.context.collection.name

            empty = bpy.data.objects.new('Bars.000', None)
            bpy.data.collections[collection].objects.link(empty)
            empty.empty_display_type = 'ARROWS'
            empty.empty_display_size = 2
            empty.show_in_front = True

            empty.location = scene.cursor.location

            for num in range(0, barchoice):
                mesh = bpy.data.meshes.new('SoundBar.000')
                object = bpy.data.objects.new('SoundBar.000', mesh)
                object.data.materials.append(material)
                mesh.from_pydata(verts, [], faces)
                mesh.update(calc_edges=True)

                bpy.data.collections[collection].objects.link(object)

                object.select_set(1)
                heightpos = -(height/2) if scene.halfheight else 0
                object.location = Vector((0,
                                         -((arealength/2)-(movedistance*num)) +
                                         (width/2),
                                         heightpos))
                # TODO: Implement option to not divide height in half in order
                # to scale from base of bars (also move down half the height
                # in the case of the default camera setup)
                bpy.ops.object.transform_apply()
                context.scene.cursor.location = \
                    (0, -((arealength/2)-(movedistance*num))+(width/2), 0)
                # origin to cursor
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                # cursor reset
                context.scene.cursor.location = (0, 0, 0)
                object.select_set(0)
                object.parent = empty

        return {'FINISHED'}


class EasyBake(Operator):
    bl_idname = 'tool.easy_bake'
    bl_label = 'Bake sound'
    bl_context = 'tool'
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(subtype='FILE_PATH', name="filepath_value")
    objectname: StringProperty(name="object_value")

    def execute(self, context):
        object = bpy.data.objects.get(self.objectname)
        empties = sound_bake.bake(context, object, self.filepath)

        if empties:
            for x in empties:
                context.view_layer.objects.active = x.parent
                bpy.ops.object.frequency_assign(freqobjname=x.name)

        # logic to handle other bakes

        return {'FINISHED'}

    # necessary for file selection
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        # TODO: make seperate function for persistant operation and easy
        # recalculation without the need for selection

        return {'RUNNING_MODAL'}


class AssignFrequency(Operator):
    bl_idname = 'object.frequency_assign'
    bl_label = 'Assign Frequency'
    bl_options = {'REGISTER', 'UNDO'}

    freqobjname: StringProperty(name="freqobjname_value")

    def execute(self, context):
        object = bpy.data.objects.get(self.freqobjname)
        recipient = context.active_object
        datapath = ''
        dataindex = 0

        if recipient.dataoptions:
            datapath = recipient.dataoptions[:-2]
            dataindex = int(recipient.dataoptions[-1:])

        if not datapath:
            if object.dataoptions:
                datapath = object.dataoptions[:-2]
                dataindex = int(object.dataoptions[-1:])

        if not datapath:
            datapath = 'scale'
            dataindex = 2
        # to prevent code errors/create necessary components
        # All objects have this but produce none if empty
        if not recipient.animation_data:
            recipient.animation_data_create()
            recipient.animation_data.action = \
                context.blend_data.actions.new(
                    object.animation_data.action.name + '_Copy')
        elif not recipient.animation_data.action:
            recipient.animation_data.action = \
                context.blend_data.actions.new(
                    object.animation_data.action.name+'_Copy')

        # This is pretty hacky? might break # TODO: Fix?
        options = \
            recipient.bl_rna.dataoptions[1].get("items")(None, bpy.context)

        foundcurve = \
            recipient.animation_data.action.fcurves.find(
                datapath, index=dataindex)

        if not foundcurve:
            if options:
                if datapath+" "+dataindex not in [x[0] for x in options]:
                    rfcurve = \
                        recipient.animation_data.action.fcurves.new(
                            datapath, index=dataindex)
                else:
                    try:
                        rfcurve = \
                            recipient.animation_data.action.fcurves.new(
                                datapath, index=dataindex)
                    except e as Exception:
                        # TODO: replace with logging
                        print("Something went wrong \n {0}".format(e))
            else:
                rfcurve = \
                    recipient.animation_data.action.fcurves.new(
                        datapath, index=dataindex)
        else:
            rfcurve = foundcurve

        # TODO: Potentially don't need to do this, could just set
        # rfcurve = obj anim ac fc samp
        for x in object.animation_data.action.fcurves[0].sampled_points:
            rfcurve.keyframe_points.insert(x.co[0], x.co[1])

        rfcurve.convert_to_samples(rfcurve.range()[0], rfcurve.range()[1])

        return {'FINISHED'}


class delete_children(Operator):
    """ensures conditional deletion of loose script remnants"""
    bl_idname = "objects.delete"
    bl_label = "Modified Delete Operator"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        for x in object.selected_objects:
            bpy.data.objects.remove(x)
        cleanbars(cleanobjects=True)
        return {'FINISHED'}


# End Classes


# Registration

# list for shortened registration classes necessary for orders sake
datatypes = (
    FreqCollection,
)

# list for shortened registration classes
classes = (
    SoundBakeUI,
    FrequencyMenu,
    BakeProps,
    MakeCamera,
    MakeBars,
    EasyBake,
    AssignFrequency,
)


def register():
    # necessary for order sake
    for cls in datatypes:
        register_class(cls)
    propinit()
    for cls in classes:
        register_class(cls)


def unregister():  # TODO: perhaps less code? combine?
    # unloads in opposite order loaded # TODO: Uneccessary?
    for cls in reversed(classes):
        unregister_class(cls)
    # unloads in opposite order loaded # TODO: Uneccessary?
    for cls in reversed(datatypes):
        unregister_class(cls)

# End Registration

# TODO: git mv to script version
# instead of having this commented code floating here
# # for use while running in blender as script instead of as an installed addon
# if __name__ == '__main__':
# 	register()
