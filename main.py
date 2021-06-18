from __future__ import print_function

import os 
import sys

import argparse

import Gltf_Parser.gltfparser as gltfp
import testUtils

import math
import vray
import numpy as np
import tempfile

argParser = argparse.ArgumentParser("Vray GLTF", allow_abbrev=False)

argParser.add_argument('scene_file',type=str, help="Scene file")

argParser.add_argument('--render_mode',dest='render_mode', type=str, help="Rendering Mode, by default interactive; can be production or interactive")
argParser.set_defaults(render_mode='interactive')

argParser.add_argument('--noise_treshold',dest='noise_treshold', type=float, help="Noise Treshold")
argParser.set_defaults(noise_treshold=0.01)

argParser.add_argument('--size',dest='size', type=str, help="Size of render (x,y) or '(x,y)'")
argParser.set_defaults(size='(1080,1080)')

argParser.add_argument('--default_camera',dest='default_camera', action='store_true', help="Ignore file cameras and use a default one")
argParser.set_defaults(default_camera=False)

argParser.add_argument('--default_cam_look_at',dest='default_cam_look_at', type=str, help="Camera look at (x,y,z)")
argParser.set_defaults(default_cam_look_at=None)

argParser.add_argument('--default_cam_rot',dest='default_cam_rot',type = str,help = 'Default camera rotation(degrees) (x,y,z) or "(x,y,z)" around the avarage object position of the scene, other brackets work too')
argParser.set_defaults(default_cam_rot='(0,0,0)')

argParser.add_argument('--default_cam_moffset',dest='default_cam_moffset',type = str,help = 'Default camera multiplier offset (x,y,z) or "(x,y,z)", all brackets will work')
argParser.set_defaults(default_cam_moffset='(-0.3,0.1,0)')

argParser.add_argument('--default_cam_pos',dest='default_cam_pos',type = str,help = 'Default camera Pos (x,y,z) or "(x,y,z)", other default cam still work but relative on this position')
argParser.set_defaults(default_cam_pos=None)

argParser.add_argument('--default_cam_fov',dest='default_cam_fov',type = float,help = 'Default camera FOV is degrees')
argParser.set_defaults(default_cam_fov=45.0)

argParser.add_argument('--default_cam_zoom',dest='default_cam_zoom',type = float,help = 'Default camera Zoom -inf to 1.0 as 1.0 max zoom')
argParser.set_defaults(default_cam_zoom=0.0)

argParser.add_argument('--default_cam_view', dest='default_cam_view', type = str, help = 'Default camera view, one of front, back, left, right, top, bottom or auto')
argParser.set_defaults(default_cam_view='auto')

argParser.add_argument('--test_material', dest='test_material', action='store_true',help = 'Use testing materials, made to see mesh vertecies and triangles')
argParser.set_defaults(test_material=False)

argParser.add_argument('--json_dump',dest='json_dump',action='store_true', help="Dump json data file contents into json. Used to debug .glb files")
argParser.set_defaults(json_dump=False)

argParser.add_argument('--num_frames',dest='num_frames',type = int, help="Set number of frames to render")
argParser.set_defaults(num_frames=0)

argParser.add_argument('--start_frame',dest='start_frame',type = int, help="Offset from the 0 frame")
argParser.set_defaults(start_frame=0)

argParser.add_argument('--animation_fps',dest='animation_fps',type = int, help="Set animation fps for whole scene. Default is 60")
argParser.set_defaults(animation_fps=60)

argParser.add_argument('--output_file',dest='output_file',type = str, help="Location to save output file, can contain file extension, if not it defaults to exr. " +
																		"If not provided file will be saved in the same folder as the scene")
argParser.set_defaults(output_file=None)

argParser.add_argument('--output_vrscene',dest='output_vrscene',type = str, help="Location to save a .vrscene file which can be rendered.")
argParser.set_defaults(output_vrscene=None)

argParser.add_argument('--default_lights',dest='default_lights', action='store_true', help="default lights")
argParser.set_defaults(default_lights=False)

argParser.add_argument('--ground_plane',dest='ground_plane', action='store_true', help="Add a ground plane")
argParser.set_defaults(ground_plane=False)

argParser.add_argument('--thick_glass',dest='thick_glass', action='store_true', help="For alpha mode set to BLEND, use thick glass, otherwise use opacity")
argParser.set_defaults(thick_glass=False)

argParser.add_argument('--thin_glass',dest='thin_glass', action='store_true', help="For alpha mode set to BLEND, use thin glass, otherwise use opacity")
argParser.set_defaults(thin_glass=False)

argParser.add_argument('--trace_depth',dest='trace_depth', type=int, help="Set the maximum reflection/refraction trace depth")
argParser.set_defaults(trace_depth=8)

argParser.add_argument('--environment_scene',dest='environment_scene', type=str, help=".vrscene file to load with additional geometry and lights")
argParser.set_defaults(environment_scene=None)

args = argParser.parse_args()

#this way it can be written in any way, as a tuple/list/array or just plain white space separation
args.default_cam_rot = tuple(eval(args.default_cam_rot))
if len(args.default_cam_rot) >3 or len(args.default_cam_rot) <3:
	raise argparse.ArgumentTypeError("Default camera angles must be (x,y,z)")

args.default_cam_moffset = tuple(eval(args.default_cam_moffset))
if len(args.default_cam_moffset) >3 or len(args.default_cam_moffset) <3:
	raise argparse.ArgumentTypeError("Default camera moffset must be (x,y,z)")

args.size = tuple(eval(args.size))
if len(args.size) >2 or len(args.size) <2:
	raise argparse.ArgumentTypeError("Size must be (x,y)")

if args.default_cam_pos != None:
	args.default_cam_pos = tuple(eval(args.default_cam_pos))
	if len(args.default_cam_pos) >3 or len(args.default_cam_pos) <3:
		raise argparse.ArgumentTypeError("Default camera pos must be (x,y,z)")

if args.default_cam_look_at != None:
	args.default_cam_look_at = tuple(eval(args.default_cam_look_at))
	if len(args.default_cam_look_at) >3 or len(args.default_cam_look_at) <3:
		raise argparse.ArgumentTypeError("Default camera look at must be (x,y,z)")

if __name__ == "__main__":

	Parser = gltfp.GltfParser()

	renderer = vray.VRayRenderer()

	try:
	
		def dumpMsg(renderer, message, level, instant):
				if level == vray.LOGLEVEL_ERROR:
					print("[ERROR]", message)
				elif level == vray.LOGLEVEL_WARNING:
					print("[Warning]", message)
				elif level == vray.LOGLEVEL_INFO:
					print("[info]", message)

		#always set arg options before parsing scene
		Parser.set_options(args)

		#renderer OPTS
		renderer.setImprovedDefaultSettings()
		renderer.setOnLogMessage(dumpMsg)
		renderer.renderMode = args.render_mode
		renderer.size = args.size
		renderer.setInteractiveNoiseThreshold(args.noise_treshold)
		
		# For interactive or GPU rendering, set limit for the trace depth
		settingsRTEngine=renderer.classes.SettingsRTEngine.getInstances()
		if len(settingsRTEngine)>0:
			settingsRTEngine[0].trace_depth=args.trace_depth

		# Set the units settings
		photometricSettings=renderer.classes.SettingsUnitsInfo.getInstanceOrCreate()
		photometricSettings.photometric_scale=1.0
		photometricSettings.scene_upDir=vray.Vector(0, 1, 0) # glTF is Y-up
		photometricSettings.meters_scale=1.0 # Assume 1 unit is 1 meter
		
		#parsing scene contents and creating vray plugins
		Parser.parseScene(args.scene_file,renderer, dumpToJson = args.json_dump)

		if args.output_vrscene!=None:
			renderer.export(args.output_vrscene)

		if args.num_frames > 0:
			frames = args.num_frames
		else:
			frames = math.floor(Parser.animation_time*Parser.animation_fps)
			frames = np.clip(frames,1,sys.maxsize)
		#set up frame, update animations
		Parser._setup_frame(0,renderer)

		for i in range(args.start_frame, args.start_frame+frames, 1):

			renderer.startSync()
			renderer.waitForRenderEnd()
			
			image = renderer.getImage()
			
			if frames > 1:

				if args.output_file != None:
					root, ext= os.path.splitext(args.output_file)
					_dir , filename = os.path.split(root)

					if ext == None:
						ext = '.exr'
					if filename == '' or filename.isspace():
						#get scene name
						filename = os.path.splitext(args.scene_file)[0]
					if ext == '.png':
						image.changeGamma(2.2)
					
					save_loc = _dir + filename + str(i) + ext
					print("Saving " + str(save_loc))
					image.save(str(save_loc))
				else:
					filename = os.path.splitext(args.scene_file)
					print("Saving " + str(filename[0]))
					image.save(str(filename[0]) + str(i) + ".exr")
				
				print('Image Ready, frame ' + str(renderer.frame) +
				' (sequenceEnd = ' + str(renderer.sequenceEnded) + ')')
				Parser._setup_frame(i+1,renderer)
			else:

				if args.output_file != None:
					root, ext= os.path.splitext(args.output_file)
					_dir , filename = os.path.split(root)

					if ext == None:
						ext = '.exr'
					if filename == '' or filename.isspace():
						#get scene name
						filename = os.path.splitext(args.scene_file)[0]
					
					save_loc = _dir + "/" + filename + ext
					print("Saving " + str(save_loc))
					image.save(str(save_loc))
				else:
					filename = os.path.splitext(args.scene_file)
					print("Saving " + str(filename[0]))
					image.save(str(filename[0]) + ".exr")
		#clean up after all frames
		renderer.clearScene()
		Parser.clean_up()

	except KeyboardInterrupt:
		print("Terminating Script by KeyboardInterrupt")
		renderer.clearScene()
		Parser.clean_up()
		quit()


