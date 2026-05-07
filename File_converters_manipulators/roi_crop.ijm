// Define input and output directories
inputDir = "D:/Dom/Fibrosis project/4th year data/pheno_xen_fullres_images/";
outputDir1 = "D:/Dom/Fibrosis project/4th year data/pheno_xen_fullres_images/roi1/";
outputDir2 = "D:/Dom/Fibrosis project/4th year data/pheno_xen_fullres_images/roi2/";

// Get list of files in input directory
fileList = getFileList(inputDir);

// Loop through each file
for (i = 0; i < fileList.length; i++) {
    // Check if file is a .tif or .ome.tif file
    if (endsWith(fileList[i], ".tif")) {
        
        // Construct full file paths
        inputPath = inputDir + fileList[i];
        outputPath = outputDir1 + fileList[i];
        
        // Open the image
        run("Bio-Formats Importer", "open=[" + inputPath + "] autoscale color_mode=Default rois_import=[ROI manager] specify_range view=Hyperstack stack_order=XYCZT");
        
        // Crop to specified rectangle
        makeRectangle(0, 0, 10056, 3024);
        run("Crop");
        
        // Save the cropped image
        run("Bio-Formats Exporter", "save=[" + outputPath + "] export compression=Uncompressed");
        
        // Close the image
        close();
        
        // Optional: print progress
        print("Processed: " + fileList[i]);
    }
}

print("roi1 batch processing complete!");

for (i = 0; i < fileList.length; i++) {
    // Check if file is a .tif or .ome.tif file
    if (endsWith(fileList[i], ".tif")) {
        
        // Construct full file paths
        inputPath = inputDir + fileList[i];
        outputPath = outputDir2 + fileList[i];
        
        // Open the image
        run("Bio-Formats Importer", "open=[" + inputPath + "] autoscale color_mode=Default rois_import=[ROI manager] specify_range view=Hyperstack stack_order=XYCZT");
        
        // Crop to specified rectangle
        makeRectangle(10120, 0, 9464, 3024);
        run("Crop");
        
        // Save the cropped image
        run("Bio-Formats Exporter", "save=[" + outputPath + "] export compression=Uncompressed");
        
        // Close the image
        close();
        
        // Optional: print progress
        print("Processed: " + fileList[i]);
    }
}

print("roi2 batch processing complete!");