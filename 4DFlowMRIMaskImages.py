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

                #Convert DICOM to VTI
                FileList = os.listdir(self.Args.InputFolder4DMRI)
                Nfiles = len(FileList)
                print (os.path.isdir("%s/%s"%(self.Args.InputFolder4DMRI,FileList[0])))
                print (os.path.isdir("%s/%s"%(self.Args.InputFolder4DMRI,FileList[3])))
                for i in range (0,Nfiles):
                        if os.path.isdir ("%s/%s"%(self.Args.InputFolder4DMRI,FileList[i])) == 1:
                                print ("--- Converting DICOM files to VTI:%s"%FileList[i])
                                CycleList = os.listdir("%s/%s"%(self.Args.InputFolder4DMRI,FileList[i]))
                                Ncycles = len(CycleList)
                                for j in range (0,Ncycles):
                                        AngioConvert = vtk.vtkDICOMImageReader()
                                        AngioConvert.SetDirectoryName("%s/%s/%s"%(self.Args.InputFolder4DMRI,FileList[i],CycleList[j]))
                                        AngioConvert.Update()

                                        #Write Unmasked VTI File
                                        print ("--- Writing Unmasked VTI File:%s/%s/%s"%(self.Args.InputFolder4DMRI,FileList[i],CycleList[j]))
                                        WriteVTIFile ("%s/%s/%s/RawImage_%s.vti"%(self.Args.InputFolder4DMRI,FileList[i],CycleList[j],CycleList[j]),image_slice)
                        else:
                                continue

		#Load the Angiography Images
		print ("--- Loading Angiography Image:%s"%self.Args.InputFileAngio)
		AngioImages=ReadVTIFile(self.Args.InputFileAngio)	

		#Mask the Angio Image using the 3D Model
		print ("--- Create a Masking Function Using the Images")
		MaskingFunction=self.MaskingFunction(AngioImages,Surface)

		#Apply the Mask to the Image
		print ("--- Applying the Mask to the Image")
		AngioImages=self.ApplyMaskToImage(AngioImages,MaskingFunction)
		
		#Save the VTI File 
		print ("--- Write the VTI File")
		WriteVTIFile("abc.vti",AngioImages)	
	
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

	parser.add_argument('-InputFolder4DMRI', '--InputFolder4DMRI', type=str, required=False, dest="MagnitudeFolder",help="The foldername that contains the 4DFlow Magnitude, Phase1, Phase2 and Phase3 images in dicom format")

	#Provide a path to the Angio images
	parser.add_argument('-InputFileAngio', '--InputFileAngio', type=str, required=True, dest="InputFileAngio",help="The filename that contains the Angio images in vti format")

	#Provide a path to the surface file segmented from the angio images
	parser.add_argument('-InputSurface', '--InputSurface', type=str, required=True, dest="InputSurface",help="The surface file that contains the model segmented from Angio images (likely in SimVascular)")
	
	args=parser.parse_args()
	FlowMRIMaskImages(args).Main()	
