import bpy
import sys

from math import exp, asin, pi, sqrt, log
from mathutils import (Vector, Euler)


def bake(context, object, filepath):

    scene = context.scene
    sound = bpy.ops.sound
    graph = bpy.ops.graph
    cframe = context.scene.frame_current

    if context.scene.bakefromzero:
        context.scene.frame_set(1)

    step = 0
    empties = []

    area = context.area.ui_type  # grab current area

    # in order to make an item the active item from a script it must be the
    # only one selected (There may be another way but it does function)
    bpy.ops.object.select_all(action='DESELECT')

    # kinda hacky
    if "Bars" in object.name or "SoundBar" in str(object.children):
        stepchoice = len(object.children)
        collection = bpy.context.collection

        for x in range(stepchoice):
            empty = bpy.data.objects.new('DataEmpty.000', None)
            collection.objects.link(empty)
            empty.parent = object.children[x]
            empty.parent_type = 'VERTEX'
            empties.append(empty)

        ocount = len(empties)
        # DO NOT CHANGE (unless you are me AND you know what you are doing...
        # so me, don't change it)
        czero = 16.35
        # ~16k highest frequency most can hear is 16000 - 18000 hz
        exponent = 10
        minfreq = object.minimumfrequency
        if minfreq < 20:
            minfreq = 20
        maxfreq = object.maximumfrequency
        minlog = log(minfreq/16.35, 2)
        # for operation below (even dist)
        maxlog = log(maxfreq/16.35, 2)-minlog
        dist = maxlog/ocount  # even distribution dist
        slopemod = 7.4
        targetmax = 1
        # this is for multiplication of the minimum frequency eg. 2 * 0.5
        freqgap = 0.5

        datapath = 'scale'  # TODO: Implement choices through ui
        dataindex = 2  # TODO: Implement choices through ui

        globallowpoint = 0.0
        globalhighpoint = 0.0

        for x in empties:
            freqmin = czero*(2**(step*dist+minlog))
            freqmax = freqmin+(freqmin*freqgap)
            # for documenting
            freqrange = str(round(freqmin))+" - "+str(round(freqmax))

            if not scene.frequencyoptions.get(freqrange):
                # TODO: Implement
                # if not scene.frequencyoptions.get(filename):
                y = scene.frequencyoptions.add()
                y.objname = x.name
                y.range = freqrange

            bpy.context.area.ui_type = 'FCURVES'  # required for ops context

            # z axis scale keyframe at frame 0
            x.keyframe_insert(data_path=datapath, index=dataindex, frame=0)
            x.select_set(1)  # required for ops context

            graph.sound_bake(
                filepath=filepath, high=freqmax, low=freqmin,
                attack=scene.bakeattack, release=scene.bakerelease)

            # This section is for setting local scale, better representation
            # of single item frequency range
            highpoint = 0.0  # in case it doesn't get set below
            lowpoint = 0.0  # in case it doesn't get set below

            rfcurve = \
                x.animation_data.action.fcurves.find(datapath, index=dataindex)
            rfcurve.convert_to_keyframes(rfcurve.range()[0],
                                         rfcurve.range()[1])

            for point in rfcurve.keyframe_points:
                if point.co[1] > highpoint:  # collecting local info
                    highpoint = point.co[1]
                if point.co[1] < lowpoint:
                    lowpoint = point.co[1]

            if highpoint > globalhighpoint:  # collecting global info
                globalhighpoint = highpoint
            if lowpoint < globallowpoint:
                globallowpoint = lowpoint

            # TODO: add ability to set beginning/end ?
            rfcurve.convert_to_samples(rfcurve.range()[0], rfcurve.range()[1])

            x.select_set(0)
            x.hide_viewport = True
            step += 1

        # global smoothing
        if not globallowpoint == 0.0 and not globalhighpoint == 0.0:

            for x in empties:
                rfcurve = \
                    x.animation_data.action.fcurves.find(datapath,
                                                         index=dataindex)
                rfcurve.convert_to_keyframes(rfcurve.range()[0],
                                             rfcurve.range()[1])

                # similar method to above but has the advantage of globally
                # scaling instead of creating mismatched bars
                for point in rfcurve.keyframe_points:
                    newpoint = \
                        (point.co[1]-globallowpoint) /\
                        (globalhighpoint - globallowpoint)
                    rfcurve.keyframe_points.insert(point.co[0], newpoint)

                # TODO: add ability to set beginning/end ?
                rfcurve.convert_to_samples(rfcurve.range()[0],
                                           rfcurve.range()[1])

    else:
        attack = object.bakeattack
        release = object.bakerelease
        freqh = object.frequencystart
        freql = object.frequencyend

        context.area.type = "GRAPH_EDITOR"
        context.view_layer.objects.active = object

        y = scene.frequencyoptions.add()
        y.objname = object.name
        y.range = str(round(freql))+" - "+str(round(freqh))

        object.select_set(1)

        dcpath = object.dataoptions[:-2]
        dcindex = int(object.dataoptions[-1:])

        object.keyframe_insert(data_path=dcpath, index=dcindex, frame=0)
        graph.sound_bake(filepath=filepath, high=freqh, low=freql,
                         attack=attack, release=release)

    context.area.ui_type = area  # reset back to original area
    context.scene.frame_set(cframe)

    if empties:
        return empties
