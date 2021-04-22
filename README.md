# Easy Bake
Blender addon for easier audio visualization

```
Quick Instructions

0. Open Blender, Destroy the child (Delete the Default "Cube" [highlight/press x/delete])
1. Download the Addon ZIP
2. Enable the Addon
	2a. Open Blender, Navigate to Edit > Preferences
	2b. Click the left tab named Add-ons
	2c. Click the top right button "Install..."
	2d. Navigate to the ZIP file, click "Install Add-on"
	2e. Make sure the box next to "Tool: Easy Sound Bake" in the center of the window is checked.
3. Return to the 3D View, Make sure the Sidebar is open (Keyboard Shortcut N)
4. In the Sidebar select the "Misc" tab on the right
5. Click "Create Bars"
6. Click "Camera/Reposition Camera"
7. Press `(~) on the Keyboard and move the mouse to "View Camera" (Numpad 0)
6. You can easily undo and then customize height, width, and number of bars

Each time you click "Create Bars" it will create a new set of bars, movable by the array object in the center of the bar collection.
```

&nbsp;

-----------------------------------------------
###### &emsp; Addon operation (more to come)
-----------------------------------------------

&nbsp;

* When you select an object it will now have the "Bake Properties" section in the property pane under Object Properties

* If you keyframe an object it will give you the option to select the keyframe "Path" in the "Bake Properties" section

* The "Frequency" dropdown applies a known set of keyframe points to the object INSTEAD of baking (I will make this more obvious in a future iteration of the plugin)

* Influence doesn't do anything yet

* If "Bake from Frame 0" is not selected it will bake from the current playhead frame onward

&nbsp;

---

### ToDo List

> This will be separated into a features/planned features list

&nbsp;


- [ ] **Make things more pretty**

&nbsp;

- [x] : Fix Collection grabbing to create in current collections
- [x] : Create duplicater/easy way to duplicate bar systems
- [x] : Create/figure out way to apply material easily to all objects within heirarchy
- [ ]  apply material logic that doesn't overwrite material unless it shared the same material beforehand
- [ ] Fix UI layout to be more streamlined/seperated (UI Update)
- [x] add bake from zero prop to all UI areas
- [ ] create property for object array handling with frequency spacing function from collection (custom bar type animation)
- [ ] Test and create circular/curvable bar setup
- [ ] revisit smoothing algorithm in sound_bake.py
- [ ] create seperate frequency spacing function
- [ ] figure out how to do background processing of sound baking function
- [x] Make it clear that the custom range must be baked and is seperate from selecting an existing frequency
- [x] Round Frequencies displayed in frequency object options
- [ ] Error handling for invalid selections
- [ ] logging for plugin
- [ ] documentaction
- [ ] extensive documentation
- [ ] Error handling for unexpected values (say, low freq exceeds high freq)
- [ ] Handle overwrite of existing curves
- [ ] Handle more than one animation curve on an object
- [ ] Handle blender operation context errors and create function to put screen space back to previous in case of ilure
- [ ] Create sound file property
- [ ] Create button for using other sounds files while sound file prop is filled (aka bypass/re-select)
- [ ] add common path context for loc rot scl (or perhaps simply import basic keyframe menu)
- [ ] create scale information collection logic to better apply scaling to data influence (wtf me?)
- [ ] create 3d bar viz preset (for max cheese)
- [ ] create preset creation classes
- [x] create deletion logic to better clean objects
- [x] clean objects function
- [x] update function when object is deleted to trigger clean function?
- [ ] do an insane sweep of plugin logic and ensure no toes would be stepped upon during normal plugin operation
- [ ] more unique naming scheme for objects created by plugin for easier cleaning?
- [ ] more streamlined function for using objects as a bar system?
- [x] bars that move only up/down? (bars originating from base insead of center)
- [ ] triangles (???)
- [ ] Add option for frame limiting on animation data transfer
- [ ] rfcurve management system (in the case of multiple)

### Potentially Not Feasible

> Research Required

- [ ] Create menu classes for easy adding
- [ ] Add material context to bars empty?
- [ ] Create influence slider update function
- [ ] Add background processing for frequency application func
