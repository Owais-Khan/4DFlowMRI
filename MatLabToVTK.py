import os
import numpy as np
import scipy.io
import vtk
import argparse
from glob import glob
from utilities import *
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk
import h5py

class MatLabToVTK():
	def __init__(self,Args):
		self.Args=Args
		if self.Args.OutputFolder is None:
			InputFileName=self.Args.InputFileName.split("/")[-1]
			self.Args.OutputFolder=self.Args.InputFileName.replace(InputFileName,"")+"./VTK_Files"
			os.system("mkdir %s"%self.Args.OutputFolder)
			print ("\n The OutputFolder is: %s"%self.Args.OutputFolder)

	def Main(self):
		print ("\n Reading the Matlab File...")
		#Data = scipy.io.loadmat(self.Args.InputFileName)
		Data  = h5py.File(self.Args.InputFileName, 'r')
		
		print ("\n--- Data in the Matlab File:")
		for key in Data.keys(): print ("------ %s"%key)

		#Convert Data into Numpy Array format
		#print ("\n--- Converting Dictionary to Numpy Format")
		#PCMR = np.array(Data["PCMR"]).T
		
		#Obtain the temporal array
		Time=sorted(np.unique(Data["PCMR"][3]))
		No_TimeSteps=len(Time)
		print ("\n")
		print ("------ Length of Time Array: %d"%No_TimeSteps)
		print ("------ Temporal Resolution : %.05f"%Time[1])
		Total_Points=Data["PCMR"][0].shape[0]
		No_Coordinates=int(Total_Points/No_TimeSteps)
		print ("------ Number of Points: %d"%No_Coordinates)

	
		#Find the Dimensions of the X, Y and Z
		X_unique=sorted(np.unique(Data["PCMR"][0]))
		Y_unique=sorted(np.unique(Data["PCMR"][1]))
		Z_unique=sorted(np.unique(Data["PCMR"][2]))


		#Get the minimum and max, dimensions and resolution
		#
		#Min and Max
		minX=min(X_unique); maxX=max(X_unique)
		minY=min(Y_unique); maxY=max(Y_unique)
		minZ=min(Z_unique); maxZ=max(Z_unique)
		
		#Resolution
		X_Res=(max(X_unique)-min(X_unique))/len(X_unique)
		Y_Res=(max(Y_unique)-min(Y_unique))/len(Y_unique)
		Z_Res=(max(Z_unique)-min(Z_unique))/len(Z_unique)
		
		#Dimensions
		DimX= len(X_unique)
		DimY= len(Y_unique)
		DimZ= len(Z_unique)
		print ("\n--- Spatial Parameters:")
		print ("------ Length of X:   %d"%DimX)
		print ("------ Length of Y:   %d"%DimY)
		print ("------ Length of Z:   %d"%DimZ)
		print ("------ Spatial Res X: %.05f"%X_Res)
		print ("------ Spatial Res Y: %.05f"%Y_Res)
		print ("------ Spatial Res Z: %.05f"%Z_Res)
		print ("------ Min and Max X: %.05f %.05f"%(minX, maxX))
		print ("------ Min and Max Y: %.05f %.05f"%(minY, maxY))
		print ("------ Min and Max Z: %.05f %.05f"%(minZ, maxZ))

		#Sort by indicies to match VTK format
		x_temp=Data["PCMR"][0][0:No_Coordinates]
		y_temp=Data["PCMR"][1][0:No_Coordinates]
		z_temp=Data["PCMR"][2][0:No_Coordinates]
		sorted_indicies= np.lexsort((x_temp,y_temp,z_temp))
		
		#Create VTK Image Data
		ImageData=vtk.vtkImageData()
		ImageData.SetDimensions(DimX,DimY,DimZ)
		ImageData.SetSpacing(X_Res,Y_Res,Z_Res)
		ImageData.SetOrigin(minX,minY,minZ)
		ImageData.AllocateScalars(vtk.VTK_FLOAT,1) #Use 2 for complex image
		

		print ("\n Converting the Data to VTK format")
		for i in range(0,No_TimeSteps):
			print ("------ Looping over: %d"%i)
			velocity_=np.zeros(shape=(No_Coordinates,3))

			#Write data to numpy array
			velocity_[:,0]=np.array(Data["PCMR"][-3][No_Coordinates*i:No_Coordinates*(i+1)])[:]
			velocity_[:,1]=np.array(Data["PCMR"][-2][No_Coordinates*i:No_Coordinates*(i+1)])[:]
			velocity_[:,2]=np.array(Data["PCMR"][-1][No_Coordinates*i:No_Coordinates*(i+1)])[:]

			#Sort the indicies to match VTK format
			velocity_[:,0]=velocity_[sorted_indicies,0]
			velocity_[:,1]=velocity_[sorted_indicies,1]
			velocity_[:,2]=velocity_[sorted_indicies,2]

			#Sort the indicies for velocity based on vtk format.
			velocityMag_=np.linalg.norm(velocity_, axis=1)
			
			#Image magnitude
			magnitude_=np.array(Data["PCMR"][-3][No_Coordinates*i:No_Coordinates*(i+1)])[:]
			magnitude_=magnitude_[sorted_indicies]

	
			velocityVTK_=numpy_to_vtk(velocity_)
			velocityVTK_.SetName("Velocity")
			ImageData.GetPointData().AddArray(velocityVTK_)

			velocityMagVTK_=numpy_to_vtk(velocityMag_)
			velocityMagVTK_.SetName("Velocity_Magnitude")
			ImageData.GetPointData().AddArray(velocityMagVTK_)	
		
			magnitudeVTK_=numpy_to_vtk(magnitude_)
			magnitudeVTK_.SetName("Magnitude")
			ImageData.GetPointData().AddArray(magnitudeVTK_)

			ImageData.Modified()

			#Reflect Image if asked by the user
			if self.Args.ReflectionPlane:
				print ("--------- Reflecting Data about %s axis"%self.Args.ReflectionPlane)
				reflection_filter = vtk.vtkAxisAlignedReflectionFilter()
				reflection_filter.SetInputData(ImageData)
				if   self.Args.ReflectionPlane=="XMin": reflection_filter.SetPlaneModeToXMin()
				elif self.Args.ReflectionPlane=="YMin": reflection_filter.SetPlaneModeToYMin()
				elif self.Args.ReflectionPlane=="ZMin": reflection_filter.SetPlaneModeToZMin()
				elif self.Args.ReflectionPlane=="XMax": reflection_filter.SetPlaneModeToXMax()
				elif self.Args.ReflectionPlane=="YMax": reflection_filter.SetPlaneModeToYMax()
				elif self.Args.ReflectionPlane=="ZMax": reflection_filter.SetPlaneModeToZMax()
				else: raise Exception("Reflection plane not known: %s"%self.Args.ReflectionPlane) 
				reflection_filter.SetCopyInput(0)
				reflection_filter.Update()

			if   self.Args.FileFormat=="vti": WriteVTIFile(self.Args.OutputFolder+"/Velocity_%.03d.vti"%i,reflection_filter.GetOutput())
			elif self.Args.FileFormat=="nii.gz": WriteNIFTIFile(self.Args.OutputFolder+"/Velocity_%.03d.nii.gz"%i,ImageData)
			else: raise ExceptionName("Output file format %s not recognized"%self.Args.FileFormat)
		
			
			
if __name__=="__main__":
        #Description
	parser = argparse.ArgumentParser(description="This script will take in a volumetric dataset with X Y Z T Mag U V W array written in matlab format.")
	parser.add_argument('-InputFileName', '--InputFileName', required=True, dest="InputFileName",help="A Matlab file.")
	parser.add_argument('-OutputFolder', '--OutputFolder', required=False, dest="OutputFolder",help="The folder name where all the output velocities will be stored.")
	parser.add_argument('-FileFormat', '--FileFormat', required=False, dest="FileFormat", default="vti", help="Output file format: vti or nii.gz.")
	parser.add_argument('-ReflectionPlane', '--ReflectionPlane', required=False, dest="ReflectionPlane", default=None, help="Reflect data about X Y or Z plane")
	args=parser.parse_args()
	MatLabToVTK(args).Main()

