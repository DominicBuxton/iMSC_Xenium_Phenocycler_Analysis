//for a single image folder - Subtract the dapi channel from selected channels. Used to (ideally) remove background DNA-binding by the oligo-conjugated antibodies. Use not recommended for TFs, like FoxP3, or for images from xenium. 
folder = "path/to/folder/";//include trailing slash

//choose selected images to process
images_to_adjust = newArray("image1.tif", "image2.tif", "image3.tif");


//subtract the dapi image from the selected image - save the result 
open(folder + "dapi.tif");
dapi_title = getTitle();

for(i = 0; i < images_to_adjust.length; i++) {//for each image to adjust, open, subtract the dapi, save it, close)
	image_path = folder + images_to_adjust[i];
	open(image_path);
	image_title = getTitle();
	imageCalculator("Subtract create", image_title, dapi_title);
	//save
	selectImage("Result of " + image_title);
	save(image_path); //replace the original image with the corrected image
	print("saved" + images_to_adjust[i] + "to" + image_path);
	close("Result of " + image_title);
	close(image_title);
	};
close(dapi_title)
print("done :)")
