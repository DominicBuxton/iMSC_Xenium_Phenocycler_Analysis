//Opens channels 1 at a time, crops them and saves the result. Allows processing of images larger than ram.

path = "D:/Dom/Fibrosis project/4th year data - update location/DPOC_RBLA_XENIU_2_Scan1.er.qptiff"
numChannels = 25

for (c = 1; c<=numChannels; c++) {
	run("Bio-Formats Importer", "open=[D:/Dom/Fibrosis project/4th year data - update location/DPOC_RBLA_XENIU_2_Scan1.er.qptiff] autoscale color_mode=Default rois_import=[ROI manager] specify_range view=Hyperstack stack_order=XYCZT series_1 c_begin_1=" + c + " " + "c_end_1=" + c + " " + "c_step_1=1");
	//run("Brightness/Contrast...");
	run("Enhance Contrast", "saturated=0.35");
	setMinAndMax(377, 2642);
	//edit based on ROI
	makeRectangle(1056, 11472, 19584, 3024);
	run("Crop");
	run("Rotate 90 Degrees Right");
	run("Rotate 90 Degrees Right");
	save_path = "D:/Dom/Fibrosis project/4th year data - update location/pheno_fullres_individual_channels/pheno_C" + c + ".ome.tif";
	options = "save=[" + save_path + "] export compression=Uncompressed";
	run("Bio-Formats Exporter", options);
	close;
	print("saved channel" + c + "to" + save_path);
}

print("saved all channels :)")