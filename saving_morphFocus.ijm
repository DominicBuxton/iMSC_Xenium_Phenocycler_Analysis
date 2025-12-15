//scales, crops, and saves individual morphology_focus.ome.tif files from Xenium outputs
//requires dimensions of phenocycler image you want to register with

inputDir = "D:/Dom/Fibrosis project/4th year data/output-XETG00160__0075879__Region_8__20250731__143804/morphology_focus";
outputDir = "D:/Dom/Fibrosis project/4th year data/xen_pheno_region8/";
pheno_width = 18720;
pheno_height = 2496;
save_path1 = outputDir + "xen_dapi.ome.tif";
save_path2 = outputDir + "xen_ATP_cad_cd45.ome.tif";
save_path3 = outputDir + "xen_18s.ome.tif";
save_path4 = outputDir + "xen_alphasma_vimentin.ome.tif";

// Get list of files in input directory
fileList = getFileList(inputDir);
fileList = Array.sort(fileList);
for (i = 0; i<=3; i++) {
	print(fileList[i]);
}
// Define your channel variable (you'll need to set this)
c = 1; // or whatever channel you want

// Open, scale, save dapi channel
filePath = inputDir + "/" + fileList[0];
run("Bio-Formats Importer", "open=[" + filePath + "] autoscale color_mode=Default rois_import=[ROI manager] specify_range view=Hyperstack stack_order=XYCZT series_1 c_begin_1=" + c + " c_end_1=" + c + " c_step_1=1");
imgHeight = getHeight();
imgWidth = getWidth();
scaleHeight = imgHeight/(imgWidth/pheno_width);
run("Scale...", "x=- y=- width=phenowidth height=scaleHeight interpolation=Bilinear average create");

//defining dimensions of your crop
waitForUser("Work out where your y-offset should be");
Dialog.create("Enter yoffset");
Dialog.addMessage("Please enter the yoffset value based on the open image:");
Dialog.addNumber("yoffset:", 0);
Dialog.show();
yoffset = Dialog.getNumber();
makeRectangle(0, yoffset, pheno_width, pheno_height);
run("Crop");
options = "save=[" + save_path1 + "] export compression=Uncompressed";
run("Bio-Formats Exporter", options);
close("*")

c=2;
// Open, scale, save ATP/cad/cd45 channel
filePath = inputDir + "/" + fileList[1];
run("Bio-Formats Importer", "open=[" + filePath + "] autoscale color_mode=Default rois_import=[ROI manager] specify_range view=Hyperstack stack_order=XYCZT series_1 c_begin_1=" + c + " c_end_1=" + c + " c_step_1=1");
run("Scale...", "x=- y=- width=phenowidth height=scaleHeight interpolation=Bilinear average create");
makeRectangle(0,yoffset, pheno_width, pheno_height);
run("Crop");
options = "save=[" + save_path2 + "] export compression=Uncompressed";
run("Bio-Formats Exporter", options);
close("*")

c=3;
// Open, scale, save 18s channel
filePath = inputDir + "/" + fileList[2];
run("Bio-Formats Importer", "open=[" + filePath + "] autoscale color_mode=Default rois_import=[ROI manager] specify_range view=Hyperstack stack_order=XYCZT series_1 c_begin_1=" + c + " c_end_1=" + c + " c_step_1=1");
run("Scale...", "x=- y=- width=phenowidth height=scaleHeight interpolation=Bilinear average create");
makeRectangle(0,yoffset, pheno_width, pheno_height);
run("Crop");
options = "save=[" + save_path3 + "] export compression=Uncompressed";
run("Bio-Formats Exporter", options);
close("*")

c=4;
// Open, scale, save vimentin channel
filePath = inputDir + "/" + fileList[3];
run("Bio-Formats Importer", "open=[" + filePath + "] autoscale color_mode=Default rois_import=[ROI manager] specify_range view=Hyperstack stack_order=XYCZT series_1 c_begin_1=" + c + " c_end_1=" + c + " c_step_1=1");
run("Scale...", "x=- y=- width=phenowidth height=scaleHeight interpolation=Bilinear average create");
makeRectangle(0,yoffset, pheno_width, pheno_height);
run("Crop");
options = "save=[" + save_path4 + "] export compression=Uncompressed";
run("Bio-Formats Exporter", options);
close("*")