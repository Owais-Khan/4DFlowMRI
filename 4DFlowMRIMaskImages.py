import vtk
import numpy
import argparse
from glob import glob
import os
from utilities import *

class FlowMRIMaskImages():
	def __init__(self,Args):
		self.Args=Args

	def Main(self):
		
		#Load the 3D Surface
		print ("--- Loading Surface File:%s"%self.Args.InputSurface)
		Surface=ReadVTPFile(self.Args.InputSurface)
		 #Load the 3D Surface
                
		print ("--- Loading Surface File:%s"%self.Args.InputSurface)
		Surface=ReadVTPFile(self.Args.InputSurface)

		print ("--- Converting Dicoms to VTI Stacks")
		OutFileNames=self.ConvertDicomsToVTI()		
		
		for OutFileName_ in OutFileNames:
			#Load the Angiography Images
			print ("--- Loading Angiography Image:%s"%OutFileName_)
			Image_=ReadVTIFile(OutFileName_)

			#Scale the Image to correct origin and to cm instead of mm
			ImageScaled_=ScaleImage(Image_)
			

			#Save the Scaled Image
			WriteVTIFile(OutFileName_,ImageScaled_)
	

			#Mask the Angio Image using the 3D Model
			print ("--- Create a Masking Function Using the Images")
			MaskingFunction=self.MaskingFunction(ImageScaled_,Surface)

			#Apply the Mask to the Image
			print ("--- Applying the Mask to the Image")
			AngioImages=self.ApplyMaskToImage(ImageScaled_,MaskingFunction)
		
			#Save the VTI File 
			print ("--- Write the VTI File")
			WriteVTIFile(OutFileName_.replace("RawImage","RawImageMasked"),ImageScaled_)	


	def ConvertDicomsToVTI(self):
		FolderList=[]
		OutFileList=[]
		for Tag in ["Magnitude","Phase1","Phase2","Phase3"]:
			FolderList = FolderList + sorted(glob("%s/%s/*"%(self.Args.InputFolder4DMRI,Tag)))
		
		print ("------ Number of Folders Detected: %d"%len(FolderList))
	
		NFolders= len(FolderList)
		for i in range (0,NFolders):
			os.system("rm %s/*.vti"%FolderList[i])
			
			print ("------ Looping over: %s"%FolderList[i])
			#AngioConvert_ = vtk.vtkDICOMImageReader()
			#AngioConvert_.SetDirectoryName(FolderList[i])
			#AngioConvert_.Update()
				
			#Cycle Number
			CycleNo_=int(FolderList[i].split("_")[-1])
	
			#Give an Outfile Name
			OutFileName_=FolderList[i]+"/RawImage_%d.vti"%CycleNo_
			
			OutFileList.append(OutFileName_)

			#Write Unmasked VTI File
			#print ("------ Writing the unmasked VTI File: %s"%OutFileName_)
			#WriteVTIFile (OutFileName_,AngioConvert_.GetOutput())
			
			#Just take one file from the folder
			infile_=glob(FolderList[i]+"/*.IMA")+glob(FolderList[i]+"/*.dcm")
		
			os.system("vmtkimagewriter -ifile %s -ofile %s"%(infile_[0],OutFileName_))	
			return OutFileList
	def ApplyMaskToImage(self,AngioImages,MaskingFunction):
		Npts=AngioImages.GetNumberOfPoints()
		for i in range(0,Npts):
			if MaskingFunction.IsInside(i)==0:
				AngioImages.GetPointData().GetArray("Scalars_").SetValue(i,1000000)
			else:
				counter+=1
		return AngioImages

	def MaskingFunction(self,AngioImages,Surface):
		
		Npts=AngioImages.GetNumberOfPoints()

		#Create an array that has all of the points
		print ("------ Extracting Points from Image Data")
		ImagePoints = vtk.vtkPoints()
		for i in range(Npts):
			point_=AngioImages.GetPoint(i)
			ImagePoints.InsertNextPoint(point_[0],point_[1],point_[2])

		#Createa a vtk point data function to store the point data
		ImagePointsVTK=vtk.vtkPolyData()
		ImagePointsVTK.SetPoints(ImagePoints)
	
		#Check if point is inside a surface
		print ("------ Checking if Image Points are inside the Surface")
		selectEnclosed = vtk.vtkSelectEnclosedPoints()
		selectEnclosed.SetInputData(ImagePointsVTK)
		selectEnclosed.SetSurfaceData(Surface)
		selectEnclosed.Update()		

		return selectEnclosed 

if __name__=="__main__":
        #Description
	parser = argparse.ArgumentParser(description="This script will mask the Aniography, Magnitude and Phase images using the 3D surface model segmented in SimVascular")

	parser.add_argument('-InputFolder4DMRI', '--InputFolder4DMRI', type=str, required=True, dest="InputFolder4DMRI",help="The foldername that contains the 4DFlow Magnitude, Phase1, Phase2 and Phase3 images in dicom format")

	#Provide a path to the Angio images
	parser.add_argument('-InputFileAngio', '--InputFileAngio', type=str, required=False, dest="InputFileAngio",help="The filename that contains the Angio images in vti format")

	#Provide a path to the surface file segmented from the angio images
	parser.add_argument('-InputSurface', '--InputSurface', type=str, required=True, dest="InputSurface",help="The surface file that contains the model segmented from Angio images (likely in SimVascular)")
	
	args=parser.parse_args()
	FlowMRIMaskImages(args).Main()	
