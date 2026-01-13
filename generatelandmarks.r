#generating landmark sets for systematic registration investigation

#read in your ground truth landmark dataset
xen_gtLandmarks = read.csv("D:/Dom/Fibrosis project/4th year data/xen_pheno_registration/systematising landmarks/Landmark csvs/50gt_xen_roi1.csv")
pheno_gtLandmarks = read.csv("D:/Dom/Fibrosis project/4th year data/xen_pheno_registration/systematising landmarks/Landmark csvs/50gt_pheno_roi1.csv")

#specify the number of landmarks you want. You can create multiple sets with different numbers of landmarks
num_landmarks = c(5, 10 , 15, 30)

#specify the folder you want to save your files to
output_dir = "D:/Dom/Fibrosis project/4th year data/xen_pheno_registration/systematising landmarks/Landmark csvs"

#specify the naming convention of your files. By default they will be "output_dir + num_landmarks + xenname/phenoname"
xenname = "_xen_spaced_roi1.csv"
phenoname = "_pheno_spaced_roi1.csv"

for (n in num_landmarks) {
  rkey = c()
  landmarks_per_section = (50-n)/5
  x = 1
  while (x<=landmarks_per_section){
    index = seq(x, 50, 10)
    rkey = append(rkey, index)
    x= x+1
  }
  print(rkey)
  xen_spaced = xen_gtLandmarks[-rkey,]
  pheno_spaced = pheno_gtLandmarks[-rkey,]

  xenpath = paste0(output_dir, "/", as.character(n), xenname)
  phenopath = paste0(output_dir, "/", as.character(n), phenoname)
  write.csv(xen_spaced, xenpath)
  write.csv(pheno_spaced, phenopath)
}
