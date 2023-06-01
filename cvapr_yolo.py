import glob
import pathlib
import os
from PIL import Image

#Run training - probably to be skipped as we used colab
#os.system('''python3 ./yolov7/train.py --batch 16 --epochs 600 --data data/coco.yaml --weights 'yolov7.pt' --cfg cfg/training/yolov7-carparts.yaml --device 0 --cache-images --workers 8 --save_period 1''')#--resume

# Run evaluation
print(pathlib.Path(__file__).parent.absolute())
path = str(pathlib.Path(__file__).parent.absolute()) + '/yolov7/'

os.chdir(path)
#model script name
detectFile = path + 'detect.py'
#(param) directory to pretrained headers
epochFile = path + 'runs/train/epok600/weights/best.pt'
#(param) detection precission
detectionPrecission = str(0.1)
#(param) input directory
imagesFolder = path + 'YOLO-image-recognition-1/test/images/' #single image also here
os.system('python ' + detectFile + ' --weights ' + epochFile + ' --conf ' + detectionPrecission + ' --source ' + imagesFolder)

#(can be param, but we would need to change model a bit) directory where the results are <- default the every detectoon has exp and number folder e.g. exp, exp1, exp2, exp3... it can be changed
#results in .\yolov7\runs\detect\exp...
resultsFolder = path + '/runs/detect/exp5/' 
#display results on all test images
for imageName in glob.glob(resultsFolder + '*.jpg'): #assuming JPG
    img = Image.open(imageName)
    img.show()
