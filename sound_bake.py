# \frac{K}{(1+\exp(\frac{b}{2}-b\cdot\frac{j\left[x\right]}{m}))}
# \frac{\max\left(k\right)}{1+\exp\left(\left(\max\left(k\right)\left(\frac{b}{2}\right)\right)-\left(b\cdot k\left[d\right]\right)\right)} #doesn't work well due to exp() limiations
# Code rep K/(1+exp(b/2-b*(x/m)))
# https://www.desmos.com/calculator/7fo9sfswgl
# ((math.asin(x/max*0.5-1))/(math.pi/max))+max*0.5
# https://www.desmos.com/calculator/5av4jiaexe
# the not dumb way^
# https://www.desmos.com/calculator/ysusjmj0ly
# smoothing algorithm

import bpy
import sys

from math import exp, asin, pi, sqrt, log
from mathutils import ( Vector, Euler )

def bake(context, object, filepath) :

	scene = context.scene
	sound = bpy.ops.sound
	graph = bpy.ops.graph
	cframe = context.scene.frame_current

	if context.scene.bakefromzero :
		context.scene.frame_set(1)

	step = 0
	empties = []

	area = context.area.ui_type # grab current area

	# in order to make an item the active item from a script it must be the only one selected (There may be another way but it does function)
	bpy.ops.object.select_all(action='DESELECT')


	if "Bars" in object.name or "SoundBar" in str(object.children) : #kinda hacky
		stepchoice = len(object.children)
		collection = bpy.context.collection

		for x in range(stepchoice) :
			empty = bpy.data.objects.new('DataEmpty.000', None)
			collection.objects.link(empty)
			empty.parent = object.children[x]
			empty.parent_type = 'VERTEX'
			empties.append(empty)


		ocount = len(empties)
		czero = 16.35 # DO NOT CHANGE (unless you are me AND you know what you are doing... so don't change it, me)
		exponent = 10 # ~16k highest frequency most can hear is 16000 - 18000 hz
		# base = 128 # ~16k highest frequency most can hear is 16000 - 18000 hz
		# base = 90 # ~16k highest frequency most can hear is 16000 - 18000 hz
		# exponent = 10.3 # ~20khz if minfreq is A0 = 16.35 (440 12-TET)
		# exponent = 10 # ~16khz if minfreq is A0 = 16.35 (440 12-TET)
		# maxfreq = minfreq+(base**2)
		minfreq = object.minimumfrequency
		if minfreq < 20 : minfreq = 20
		maxfreq = object.maximumfrequency
		minlog = log(minfreq/16.35,2)
		maxlog = log(maxfreq/16.35,2)-minlog # for operation below (even dist)
		# resfreq = maxfreq-minfreq
		dist = maxlog/ocount #even distribution dist
		# dist = resfreq/ocount #even distribution dist
		# dist = exponent/ocount #dist for TET distribution
		# dist = ocount/base #alt dist for TET distribution
		slopemod = 7.4
		targetmax = 1
		# freqgap = (minfreq*(2**dist))/2 # original
		freqgap = 0.5 #this is for multiplication of the minimum frequency eg. 2 * 0.5

		datapath = 'scale' # TODO: Implement choices through ui
		dataindex = 2 # TODO: Implement choices through ui

		globallowpoint = 0.0
		globalhighpoint = 0.0

		for x in empties :
			#dist is the maxfreq divided by the number of bars maxfreq is around 16k
			# freqmin = (asin(((minfreq*(2**(step*dist)))/(maxfreq*0.5)-1))/(pi/maxfreq)+maxfreq*0.5)-step*freqgap
			# freqmax = (asin(((minfreq*(2**((step+1)*dist)))/(maxfreq*0.5)-1))/(pi/maxfreq)+maxfreq*0.5)+step*freqgap
			#dist is the maxfreq divided by the number of bars maxfreq is around 16k
			# freqmin = (asin(((minfreq+((step*dist)**2))/(maxfreq*0.5)-1))/(pi/maxfreq)+maxfreq*0.5)-step*freqgap
			freqmin = czero*(2**(step*dist+minlog))
			freqmax = freqmin+(freqmin*freqgap)
			freqrange = str(round(freqmin))+" - "+str(round(freqmax)) #for documenting

			if not scene.frequencyoptions.get(freqrange) :
				# if not scene.frequencyoptions.get(filename) : # TODO: Implement
				y = scene.frequencyoptions.add()
				y.objname = x.name
				y.range = freqrange

			bpy.context.area.ui_type = 'FCURVES' # required for ops context

			x.keyframe_insert(data_path=datapath, index=dataindex, frame=0) # z axis scale keyframe at frame 0
			x.select_set(1) # required for ops context

			graph.sound_bake(filepath=filepath,high=freqmax,low=freqmin,attack=scene.bakeattack,release=scene.bakerelease)

			# This section is for setting local scale, better representation of single item frequency range
			highpoint = 0.0 #in case it doesn't get set below
			lowpoint = 0.0 #in case it doesn't get set below

			rfcurve = x.animation_data.action.fcurves.find(datapath,index=dataindex)
			rfcurve.convert_to_keyframes(rfcurve.range()[0],rfcurve.range()[1])

			for point in rfcurve.keyframe_points :
				if point.co[1] > highpoint : # collecting local info
					highpoint = point.co[1]
				if point.co[1] < lowpoint :
					lowpoint = point.co[1]

			if highpoint > globalhighpoint : # collecting global info
				globalhighpoint = highpoint
			if lowpoint < globallowpoint :
				globallowpoint = lowpoint

			# # old method that produces ugly results, in order to pull off a good smoothing algorithm one would need to iterate through and compare values on the same frame
			# for point in rfcurve.keyframe_points :
			# 	newpoint = (point.co[1]-lowpoint)/(highpoint-lowpoint)
			# 	rfcurve.keyframe_points.insert(point.co[0],newpoint)

			# # this method creates a floor and ceiling slightly lower and higher than one
			# for point in rfcurve.keyframe_points :
			# 	newpoint = targetmax/(1+exp(slopemod/2-slopemod*(point.co[1])))
			# 	rfcurve.keyframe_points.insert(point.co[0],newpoint)

			# # This is here in order to not have to collect points like above
			# newlowpoint = targetmax/(1+exp(slopemod/2-slopemod*(lowpoint))) # easy grab of new min val because of above transform hp/1+exp(sm/2-sm etc.
			# newhighpoint = targetmax/(1+exp(slopemod/2-slopemod*(highpoint))) # easy grab of new max val because of above transform hp/1+exp(sm/2-sm etc.
			#
			# for point in rfcurve.keyframe_points : # same method as above comented out section
			# 	newpoint = (point.co[1]-newlowpoint)/(newhighpoint-newlowpoint)
			# 	rfcurve.keyframe_points.insert(point.co[0],newpoint)

			rfcurve.convert_to_samples(rfcurve.range()[0],rfcurve.range()[1]) # TODO: add ability to set beginning/end ?

			x.select_set(0)
			x.hide_viewport = True
			step += 1

		if not globallowpoint == 0.0 and not globalhighpoint == 0.0 : #global smoothing
			# globallowpoint = targetmax/(1+exp(slopemod/2-slopemod*(globallowpoint))) # easy grab of new min val because of above transform hp/1+exp(sm/2-sm etc.
			# globalhighpoint = targetmax/(1+exp(slopemod/2-slopemod*(globalhighpoint))) # easy grab of new max val because of above transform hp/1+exp(sm/2-sm etc.

			for x in empties :
				rfcurve = x.animation_data.action.fcurves.find(datapath,index=dataindex)
				rfcurve.convert_to_keyframes(rfcurve.range()[0],rfcurve.range()[1])

				# similar method to above but has the advantage of globally scaling instead of creating mismatched bars
				for point in rfcurve.keyframe_points :
					newpoint = (point.co[1]-globallowpoint)/(globalhighpoint-globallowpoint)
					rfcurve.keyframe_points.insert(point.co[0],newpoint)

				rfcurve.convert_to_samples(rfcurve.range()[0],rfcurve.range()[1]) # TODO: add ability to set beginning/end ?

	else :
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
		graph.sound_bake(filepath=filepath,high=freqh,low=freql,attack=attack,release=release)

	context.area.ui_type = area # reset back to original area
	context.scene.frame_set(cframe)

	if empties :
		return empties
